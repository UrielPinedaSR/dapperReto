# scrapers/scrappers.py
from abc import ABC, abstractmethod
from typing import Iterable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RawBill:
    external_id: str
    title: str
    filing_date: str | None
    summary: str | None
    pdf_urls: list[str]
    status: str | None

class BaseScraper(ABC):
    @abstractmethod
    def fetch_bills(self) -> Iterable[RawBill]:
        ...
