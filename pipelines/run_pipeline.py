# pipeline/run_pipeline.py
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .db import SessionLocal, init_db
from .models import Bill
from .transform import to_dict
from .classify import classify_sector
from scrappers.col import ColombiaScraper
import json
import logging

logger = logging.getLogger(__name__)

def upsert_bill(session, bill_dict):
    stmt = select(Bill).where(
        Bill.country == bill_dict["country"],
        Bill.external_id == bill_dict["external_id"],
    )
    existing = session.execute(stmt).scalar_one_or_none()

    if existing:
        for k, v in bill_dict.items():
            setattr(existing, k, v)
        logging.info("Updated bill %s-%s", bill_dict["country"], bill_dict["external_id"])
    else:
        session.add(Bill(**bill_dict))
        logging.info("Inserted bill %s-%s", bill_dict["country"], bill_dict["external_id"])

def run_country_colombia():
    print("Initializing database...")
    init_db()

    print("Starting scraper for Colombia...")
    scraper = ColombiaScraper()

    with SessionLocal() as session:
        print("Fetching and processing bills...")
        for raw in scraper.fetch_bills():
            bill_data = to_dict(scraper.COUNTRY, raw)

            # No Gemini por 429s
            bill_data["sector"] = "otros"

            bill_data["pdf_urls"] = json.dumps(bill_data["pdf_urls"] or [])

            upsert_bill(session, bill_data)

        session.commit()

if __name__ == "__main__":

    print("Starting pipeline for Colombia...")
    run_country_colombia()
