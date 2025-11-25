# pipeline/classify.py
import json
from google import genai

MODEL_ID = "gemini-2.5-flash"

client = genai.Client(api_key="AIzaSyA8bbtuWVDDVIcx2zVtIr3A1jaPvJUHvZ0")

SECTORS = [
    "minero-energetico",
    "servicios",
    "tecnologia",
    "agricultura",
    "financiero",
    "infraestructura",
    "salud",
    "educacion",
    "otros",
]

PROMPT = f"""
Eres un clasificador de proyectos de ley en América Latina.
Devuelve ÚNICAMENTE uno de los siguientes sectores, en minúsculas y sin explicación:
{", ".join(SECTORS)}.

Texto del proyecto:
"""

def classify_sector(title: str, summary: str | None) -> str:
    text = (title or "") + "\n\n" + (summary or "")
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=PROMPT + text[:6000],  # por si se alarga
    )
    raw = response.text.strip().lower()
    for s in SECTORS:
        if s in raw:
            return s
    return "otros"
