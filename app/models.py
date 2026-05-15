from datetime import datetime

from pgvector.sqlalchemy import Vector  # type: ignore[import-untyped]
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class QuranAyah(Base):
    __tablename__ = "quran_ayat"
    __table_args__ = (
        UniqueConstraint(
            "surah_number", "ayah_number", name="uq_quran_ayat_surah_ayah"
        ),
        CheckConstraint("ayah_number > 0", name="ck_quran_ayat_number_positive"),
        CheckConstraint(
            "length(trim(translation_text)) > 0",
            name="ck_quran_ayat_translation_text_not_empty",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    surah_number: Mapped[int] = mapped_column(nullable=False)
    ayah_number: Mapped[int] = mapped_column(nullable=False)
    translation_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    embedding: Mapped["AyahEmbedding | None"] = relationship(
        back_populates="ayah",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class AyahEmbedding(Base):
    __tablename__ = "ayah_embeddings"
    __table_args__ = (
        UniqueConstraint("quran_ayah_id", name="uq_ayah_embeddings_quran_ayah_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    quran_ayah_id: Mapped[int] = mapped_column(
        ForeignKey("quran_ayat.id", ondelete="CASCADE"),
        nullable=False,
    )
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)
    embedding_provider: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    ayah: Mapped[QuranAyah] = relationship(back_populates="embedding")
