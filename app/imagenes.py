"""
imagenes.py — Obtiene imágenes de Unsplash según el nombre del plan.
Si Unsplash no está disponible, usa Picsum como fallback.
"""

import httpx
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
UNSPLASH_URL = "https://api.unsplash.com/search/photos"

# Cache para no repetir búsquedas innecesarias
_cache = {}


def _fallback_imagen(query: str) -> str:
    """
    Genera una URL de Picsum Photos usando el query como seed.
    Siempre devuelve una imagen válida (fotos reales, sin API key).
    """
    seed = int(hashlib.md5(query.encode()).hexdigest(), 16) % 1000
    return f"https://picsum.photos/seed/{seed}/800/500"


def obtener_imagen(query: str) -> str:
    """
    Busca una imagen en Unsplash según el query.
    Si falla (rate limit, sin key, error de red), devuelve una imagen de Picsum.
    """
    if not query:
        return _fallback_imagen("actividad")

    if query in _cache:
        return _cache[query]

    if ACCESS_KEY:
        try:
            response = httpx.get(UNSPLASH_URL, params={
                "query": query,
                "per_page": 1,
                "orientation": "landscape",
                "client_id": ACCESS_KEY,
            }, timeout=5)

            if response.status_code == 200:
                data = response.json()
                resultados = data.get("results", [])
                if resultados:
                    url = resultados[0]["urls"]["regular"]
                    _cache[query] = url
                    return url
            else:
                print(f"Unsplash error {response.status_code} para '{query}' — usando Picsum")

        except Exception as e:
            print(f"Error buscando imagen en Unsplash para '{query}': {e}")

    # Fallback garantizado
    url = _fallback_imagen(query)
    _cache[query] = url
    return url