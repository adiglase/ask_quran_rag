import sqlite3
from pathlib import Path

import pytest

from app.ingest import (
    IngestionError,
    SourceColumnMapping,
    list_sqlite_columns,
    list_sqlite_tables,
    load_translated_ayat,
    prompt_source_column_mapping,
)


def test_lists_sqlite_tables_and_columns(tmp_path: Path) -> None:
    sqlite_path = tmp_path / "source.db"
    with sqlite3.connect(sqlite_path) as connection:
        connection.execute(
            "CREATE TABLE translation (sura INTEGER, ayah INTEGER, text TEXT)"
        )

    assert list_sqlite_tables(sqlite_path) == ["translation"]
    assert list_sqlite_columns(sqlite_path, "translation") == ["sura", "ayah", "text"]


def test_prompt_source_column_mapping_uses_defaults(tmp_path: Path) -> None:
    sqlite_path = tmp_path / "source.db"
    with sqlite3.connect(sqlite_path) as connection:
        connection.execute(
            """
            CREATE TABLE translation (
                sura INTEGER,
                ayah INTEGER,
                ayah_key TEXT,
                text TEXT
            )
            """
        )

    answers = iter(["", "", "", ""])
    output: list[str] = []

    mapping = prompt_source_column_mapping(
        sqlite_path,
        input_func=lambda _: next(answers),
        output_func=output.append,
    )

    assert mapping == SourceColumnMapping(
        table="translation",
        surah_column="sura",
        ayah_column="ayah",
        translation_column="text",
    )


def test_load_translated_ayat_uses_source_column_mapping(tmp_path: Path) -> None:
    sqlite_path = tmp_path / "source.db"
    with sqlite3.connect(sqlite_path) as connection:
        connection.execute(
            """
            CREATE TABLE custom_translation (
                chapter TEXT,
                verse TEXT,
                english TEXT
            )
            """
        )
        connection.execute(
            """
            INSERT INTO custom_translation (chapter, verse, english)
            VALUES ('1', '2', 'Praise belongs to Allah.')
            """
        )
        connection.execute(
            """
            INSERT INTO custom_translation (chapter, verse, english)
            VALUES ('1', '1', ' In the name of Allah. ')
            """
        )

    rows = load_translated_ayat(
        sqlite_path,
        SourceColumnMapping(
            table="custom_translation",
            surah_column="chapter",
            ayah_column="verse",
            translation_column="english",
        ),
    )

    assert len(rows) == 2
    assert rows[0].surah_number == 1
    assert rows[0].ayah_number == 1
    assert rows[0].translation_text == "In the name of Allah."


def test_load_translated_ayat_rejects_empty_translation_text(
    tmp_path: Path,
) -> None:
    sqlite_path = tmp_path / "source.db"
    with sqlite3.connect(sqlite_path) as connection:
        connection.execute(
            "CREATE TABLE translation (sura INTEGER, ayah INTEGER, text TEXT)"
        )
        connection.execute(
            "INSERT INTO translation (sura, ayah, text) VALUES (1, 1, '   ')"
        )

    with pytest.raises(IngestionError, match="empty translation text"):
        load_translated_ayat(
            sqlite_path,
            SourceColumnMapping(
                table="translation",
                surah_column="sura",
                ayah_column="ayah",
                translation_column="text",
            ),
        )


def test_load_translated_ayat_rejects_non_integer_reference(
    tmp_path: Path,
) -> None:
    sqlite_path = tmp_path / "source.db"
    with sqlite3.connect(sqlite_path) as connection:
        connection.execute(
            "CREATE TABLE translation (sura TEXT, ayah INTEGER, text TEXT)"
        )
        connection.execute(
            "INSERT INTO translation (sura, ayah, text) VALUES ('one', 1, 'Text')"
        )

    with pytest.raises(IngestionError, match="surah value"):
        load_translated_ayat(
            sqlite_path,
            SourceColumnMapping(
                table="translation",
                surah_column="sura",
                ayah_column="ayah",
                translation_column="text",
            ),
        )
