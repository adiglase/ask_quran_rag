from __future__ import annotations

import argparse
import sqlite3
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import QuranAyah


class IngestionError(Exception):
    """Raised when the source dataset cannot be imported."""


@dataclass(frozen=True)
class SourceColumnMapping:
    table: str
    surah_column: str
    ayah_column: str
    translation_column: str


@dataclass(frozen=True)
class TranslatedAyahInput:
    surah_number: int
    ayah_number: int
    translation_text: str


InputFunc = Callable[[str], str]
OutputFunc = Callable[[str], None]


def list_sqlite_tables(sqlite_path: Path) -> list[str]:
    with sqlite3.connect(sqlite_path) as connection:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

    return [str(row[0]) for row in rows]


def list_sqlite_columns(sqlite_path: Path, table: str) -> list[str]:
    with sqlite3.connect(sqlite_path) as connection:
        rows = connection.execute(f"PRAGMA table_info({_quote_identifier(table)})").fetchall()

    if not rows:
        raise IngestionError(f"Table {table!r} was not found or has no columns.")

    return [str(row[1]) for row in rows]


def load_translated_ayat(
    sqlite_path: Path, mapping: SourceColumnMapping
) -> list[TranslatedAyahInput]:
    _ensure_sqlite_path_exists(sqlite_path)

    select_sql = (
        "SELECT "
        f"{_quote_identifier(mapping.surah_column)} AS surah_number, "
        f"{_quote_identifier(mapping.ayah_column)} AS ayah_number, "
        f"{_quote_identifier(mapping.translation_column)} AS translation_text "
        f"FROM {_quote_identifier(mapping.table)}"
    )

    rows: list[TranslatedAyahInput] = []
    with sqlite3.connect(sqlite_path) as connection:
        connection.row_factory = sqlite3.Row
        try:
            source_rows = connection.execute(select_sql).fetchall()
        except sqlite3.Error as exc:
            raise IngestionError(f"Could not read mapped SQLite source: {exc}") from exc

    for index, source_row in enumerate(source_rows, start=1):
        rows.append(_coerce_source_row(source_row, index))

    if not rows:
        raise IngestionError("Mapped SQLite table did not return any rows.")

    return sorted(rows, key=lambda row: (row.surah_number, row.ayah_number))


def replace_translated_ayat(
    session: Session, translated_ayat: Sequence[TranslatedAyahInput]
) -> None:
    if not translated_ayat:
        raise IngestionError("Refusing to replace translated ayat with an empty dataset.")

    with session.begin():
        session.execute(delete(QuranAyah))
        session.add_all(
            QuranAyah(
                surah_number=row.surah_number,
                ayah_number=row.ayah_number,
                translation_text=row.translation_text,
            )
            for row in translated_ayat
        )


def prompt_source_column_mapping(
    sqlite_path: Path,
    *,
    input_func: InputFunc = input,
    output_func: OutputFunc = print,
) -> SourceColumnMapping:
    _ensure_sqlite_path_exists(sqlite_path)

    tables = list_sqlite_tables(sqlite_path)
    if not tables:
        raise IngestionError("SQLite source does not contain any user tables.")

    output_func("Found tables:")
    for index, table in enumerate(tables, start=1):
        output_func(f"{index}. {table}")

    table = _prompt_choice(
        "Which table contains the translation rows?",
        tables,
        default=_first_existing(tables, ("translation", "translations", "quran")),
        input_func=input_func,
    )

    columns = list_sqlite_columns(sqlite_path, table)
    output_func(f"\nColumns in {table}:")
    for column in columns:
        output_func(f"- {column}")

    surah_column = _prompt_choice(
        "Which column contains the surah number?",
        columns,
        default=_first_existing(
            columns, ("sura", "surah", "surah_number", "chapter", "chapter_number")
        ),
        input_func=input_func,
    )
    ayah_column = _prompt_choice(
        "Which column contains the ayah number?",
        columns,
        default=_first_existing(
            columns, ("ayah", "aya", "verse", "ayah_number", "verse_number")
        ),
        input_func=input_func,
    )
    translation_column = _prompt_choice(
        "Which column contains the translation text?",
        columns,
        default=_first_existing(
            columns, ("text", "translation", "translation_text", "content")
        ),
        input_func=input_func,
    )

    return SourceColumnMapping(
        table=table,
        surah_column=surah_column,
        ayah_column=ayah_column,
        translation_column=translation_column,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Reingest translated ayat from a SQLite translation source."
    )
    parser.add_argument("sqlite_path", type=Path)
    args = parser.parse_args(argv)

    try:
        mapping = prompt_source_column_mapping(args.sqlite_path)
        translated_ayat = load_translated_ayat(args.sqlite_path, mapping)

        print("\nThis will replace all translated ayat and delete existing embeddings.")
        if not _confirm("Continue?", input_func=input):
            print("Reingestion cancelled.")
            return 1

        with SessionLocal() as session:
            replace_translated_ayat(session, translated_ayat)

    except IngestionError as exc:
        print(f"Reingestion failed: {exc}", file=sys.stderr)
        return 1
    except SQLAlchemyError as exc:
        print(f"Reingestion failed while writing to PostgreSQL: {exc}", file=sys.stderr)
        return 1

    print(f"\nImported {len(translated_ayat):,} translated ayat.")
    print("Embeddings are absent until embedding generation runs.")
    print("Run the embedding generation command next.")
    return 0


def _coerce_source_row(row: sqlite3.Row, row_number: int) -> TranslatedAyahInput:
    try:
        surah_number = int(row["surah_number"])
    except (TypeError, ValueError) as exc:
        raise IngestionError(
            f"Row {row_number} has a surah value that is not an integer."
        ) from exc

    try:
        ayah_number = int(row["ayah_number"])
    except (TypeError, ValueError) as exc:
        raise IngestionError(
            f"Row {row_number} has an ayah value that is not an integer."
        ) from exc

    translation_text = str(row["translation_text"] or "").strip()
    if not translation_text:
        raise IngestionError(f"Row {row_number} has empty translation text.")

    return TranslatedAyahInput(
        surah_number=surah_number,
        ayah_number=ayah_number,
        translation_text=translation_text,
    )


def _prompt_choice(
    question: str,
    choices: Sequence[str],
    *,
    default: str | None,
    input_func: InputFunc,
) -> str:
    if not choices:
        raise IngestionError(f"No choices available for prompt: {question}")

    prompt = f"{question}"
    if default is not None:
        prompt += f" [{default}]"
    prompt += ": "

    while True:
        raw_answer = input_func(prompt).strip()
        if raw_answer == "" and default is not None:
            return default

        selected = _resolve_choice(raw_answer, choices)
        if selected is not None:
            return selected

        print("Please enter one of the listed names or numbers.")


def _resolve_choice(answer: str, choices: Sequence[str]) -> str | None:
    if answer.isdecimal():
        index = int(answer)
        if 1 <= index <= len(choices):
            return choices[index - 1]

    for choice in choices:
        if answer == choice:
            return choice

    return None


def _confirm(question: str, *, input_func: InputFunc) -> bool:
    answer = input_func(f"{question} [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def _first_existing(available: Sequence[str], preferred: Sequence[str]) -> str | None:
    available_by_lower = {item.lower(): item for item in available}
    for candidate in preferred:
        match = available_by_lower.get(candidate)
        if match is not None:
            return match
    if len(available) == 1:
        return available[0]
    return None


def _ensure_sqlite_path_exists(sqlite_path: Path) -> None:
    if not sqlite_path.exists():
        raise IngestionError(f"SQLite source file does not exist: {sqlite_path}")
    if not sqlite_path.is_file():
        raise IngestionError(f"SQLite source path is not a file: {sqlite_path}")


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


if __name__ == "__main__":
    raise SystemExit(main())
