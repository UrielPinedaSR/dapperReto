# scrapers/colombia.py
import requests
from bs4 import BeautifulSoup
from .scrappers import BaseScraper, RawBill

BASE_URL = "https://www.camara.gov.co/proyectos-de-ley"

class ColombiaScraper(BaseScraper):
    COUNTRY = "CO"

    def fetch_bills(self):
        resp = requests.get(BASE_URL, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Aquí adaptas al markup real de la tabla/lista
        rows = soup.select("table tbody tr")
        for row in rows:
            cols = row.find_all("td")
            # TODO: ajusta índices según estructura de la tabla
            title = cols[1].get_text(strip=True)
            external_id = cols[0].get_text(strip=True)
            filing_date = cols[2].get_text(strip=True) if len(cols) > 2 else None
            status = cols[3].get_text(strip=True) if len(cols) > 3 else None
            pdf_links = [a["href"] for a in row.select("a[href$='.pdf']")]

            yield RawBill(
                external_id=external_id,
                title=title,
                filing_date=filing_date,
                summary=None,     # si hay link de detalle, puedes hacer segundo request
                pdf_urls=pdf_links,
                status=status,
            )
