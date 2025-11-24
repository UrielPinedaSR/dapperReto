# pipeline/run_pipeline.py
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .db import SessionLocal, init_db
from .models import Bill
from .transform import to_dict
from .classify import classify_sector
from scrapers.colombia import ColombiaScraper
import json
import logging

logger = logging.getLogger(__name__)

def upsert_bill(session, bill_dict):
    # ¿existe ya?
    stmt = select(Bill).where(
        Bill.country == bill_dict["country"],
        Bill.external_id == bill_dict["external_id"],
    )
    existing = session.execute(stmt).scalar_one_or_none()

    if existing:
        # update básico (podrías comparar cambios)
        for k, v in bill_dict.items():
            setattr(existing, k, v)
        logger.info("Updated bill %s-%s", bill_dict["country"], bill_dict["external_id"])
    else:
        bill = Bill(**bill_dict)
        session.add(bill)
        logger.info("Inserted bill %s-%s", bill_dict["country"], bill_dict["external_id"])

def run_country_colombia():
    init_db()
    scraper = ColombiaScraper()
    with SessionLocal() as session:
        for raw in scraper.fetch_bills():
            bill_data = to_dict(scraper.COUNTRY, raw)
            bill_data["sector"] = classify_sector(
                bill_data["title"], bill_data.get("summary")
            )
            bill_data["pdf_urls"] = json.dumps(bill_data["pdf_urls"] or [])
            upsert_bill(session, bill_data)
        session.commit()

if __name__ == "__main__":
    run_country_colombia()
