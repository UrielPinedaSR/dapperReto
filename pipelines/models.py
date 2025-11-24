# pipeline/models.py
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, Date, Text, Integer, UniqueConstraint
from datetime import datetime

Base = declarative_base()

class Bill(Base):
    __tablename__ = "bills"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country: Mapped[str] = mapped_column(String(2), nullable=False)  # "CO", "PE"
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    filing_date: Mapped[datetime] = mapped_column(Date, nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    pdf_urls: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    status: Mapped[str] = mapped_column(String(255), nullable=True)
    sector: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("country", "external_id", name="uq_country_external"),
    )
