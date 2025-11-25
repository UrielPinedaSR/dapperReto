# scrapers/colombia.py
import requests
from bs4 import BeautifulSoup
from .scrappers import BaseScraper, RawBill

BASE_URL = "https://www.camara.gov.co/proyectos-de-ley"

class ColombiaScraper(BaseScraper):
    COUNTRY = "CO"

    def __init__(self, items_per_page: int = 50):
        self.items_per_page = items_per_page
        self.ajax_url = None
        self.nonce = None
        self.comision = ""
        self.com_locked = False
        self._load_config()

# scrapers/colombia.py
import re
import requests
from bs4 import BeautifulSoup
from .scrappers import BaseScraper, RawBill


MAIN_URL = "https://www.camara.gov.co/secretaria/proyectos-de-ley"


class ColombiaScraper(BaseScraper):
    COUNTRY = "CO"

    def __init__(self, items_per_page: int = 50):
        self.items_per_page = items_per_page
        self.ajax_url = None
        self.nonce = None
        self.comision = ""
        self.com_locked = False
        self._load_config()

    def _load_config(self):
        """Descarga la página principal y extrae PL_CFG (AJAX_URL, nonce, etc.)."""
        resp = requests.get(MAIN_URL, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        script_text = ""
        for s in soup.find_all("script"):
            if s.string and "window.PL_CFG" in s.string:
                script_text = s.string
                break

        if not script_text:
            raise RuntimeError("No se encontró la configuración PL_CFG en la página de Colombia")

        # Extraer con regex simples
        ajax_match = re.search(r'AJAX_URL:"([^"]+)"', script_text)
        nonce_match = re.search(r'PL_NONCE:"([^"]+)"', script_text)
        com_match = re.search(r'COMISION:"([^"]*)"', script_text)
        locked_match = re.search(r'COM_LOCKED:(true|false)', script_text)

        self.ajax_url = ajax_match.group(1) if ajax_match else "https://www.camara.gov.co/wp-admin/admin-ajax.php"
        self.nonce = nonce_match.group(1) if nonce_match else ""
        self.comision = com_match.group(1) if com_match else ""
        self.com_locked = locked_match.group(1) == "true" if locked_match else False

    def _fetch_page(self, page: int) -> dict:
        """Hace el POST al admin-ajax y devuelve el JSON."""
        payload = {
            "action": "get_proyectos_ley_page",
            "_ajax_nonce": self.nonce,
            "page": page,
            "per_page": str(self.items_per_page),
            "term": "",
            "comision": self.comision,
            "tipo": "All",
            "estado": "All",
            "origen": "All",
            "legislatura": "All",
        }
        if not self.com_locked:
            payload["comision_adv"] = ""

        resp = requests.post(self.ajax_url, data=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            raise RuntimeError(f"Respuesta sin success para página {page}: {data}")
        return data["data"]

    def fetch_bills(self):
        """Itera sobre todas las páginas e instancia RawBill por cada proyecto."""
        page = 1
        total_pages = 1

        while page <= total_pages:
            data = self._fetch_page(page)
            items = data.get("items", [])
            total_pages = int(data.get("total_pages", page))

            for item in items:
                # Campos que sí vimos en el JS
                nro_camara = item.get("nro_camara")
                nro_senado = item.get("nro_senado")
                external_id = str(item.get("proyecto") or item.get("titulo") or nro_camara or nro_senado or "")
                title = item.get("titulo") or item.get("proyecto") or "Proyecto de ley"

                # Estos campos dependen de cómo venga el JSON. Dejamos defensivo:
                filing_date = item.get("fecha", None)  # puede requerir parseo en transform.py
                status = item.get("estado", None)

                # La API no muestra resumen en el JS, así que lo dejamos vacío por ahora.
                summary = None

                # Guardamos al menos el link web como referencia (detalle)
                pdf_urls = []
                if item.get("link_web"):
                    pdf_urls.append(item["link_web"])

                yield RawBill(
                    external_id=external_id,
                    title=title,
                    filing_date=filing_date,
                    summary=summary,
                    pdf_urls=pdf_urls,
                    status=status,
                )

            page += 1

