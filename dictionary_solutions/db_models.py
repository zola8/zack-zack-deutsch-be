from sqlalchemy import BigInteger
from sqlalchemy import Index
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class DictionaryEntry(Base):
    __tablename__ = "dictionary"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    lang_from: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    lang_to: Mapped[str] = mapped_column(String(3), nullable=False, index=True)

    word_from: Mapped[str] = mapped_column(Text, nullable=False)
    word_to: Mapped[str] = mapped_column(Text, nullable=False)
    word_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    classification: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- GIN Trigram Indexes for fast %text% searches ---

    __table_args__ = (
        Index(
            "idx_word_from_trgm",
            "word_from",
            postgresql_using="gin",
            postgresql_ops={"word_from": "gin_trgm_ops"},
        ),
        Index(
            "idx_word_to_trgm",
            "word_to",
            postgresql_using="gin",
            postgresql_ops={"word_to": "gin_trgm_ops"},
        ),
        Index(
            "idx_classification_trgm",
            "classification",
            postgresql_using="gin",
            postgresql_ops={"classification": "gin_trgm_ops"},
        ),
    )

    def __repr__(self) -> str:
        return f"<DictEntry {self.word_from} -> {self.word_to}>"
