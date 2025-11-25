# pipeline/transform.py
from datetime import datetime
from scrappers.scrappers import RawBill

def parse_date(date_str: str | None):
    if not date_str:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

def to_dict(country: str, raw: RawBill) -> dict:
    return {
        "country": country,
        "external_id": raw.external_id,
        "title": raw.title,
        "filing_date": parse_date(raw.filing_date),
        "summary": raw.summary,
        "pdf_urls": raw.pdf_urls,
        "status": raw.status,
    }
