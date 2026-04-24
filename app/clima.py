"""
clima.py — Obtiene el clima actual usando OpenWeatherMap.
"""

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def obtener_clima(lat: float, lon: float) -> str:
    """
    Dado una latitud y longitud, devuelve el clima simplificado:
    'soleado', 'nublado' o 'lluvioso'.
    Devuelve 'cualquiera' si hay algún error.
    """
    if not API_KEY:
        return "cualquiera"

    try:
        response = httpx.get(BASE_URL, params={
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric",
            "lang": "es"
        }, timeout=5)

        data = response.json()
        condicion = data["weather"][0]["main"].lower()

        if condicion in ("rain", "drizzle", "thunderstorm"):
            return "lluvioso"
        elif condicion in ("clouds",):
            return "nublado"
        else:
            return "soleado"

    except Exception:
        return "cualquiera"


def obtener_clima_ciudad(ciudad: str) -> str:
    """
    Dado el nombre de una ciudad, devuelve el clima simplificado.
    """
    if not API_KEY:
        return "cualquiera"

    try:
        response = httpx.get(BASE_URL, params={
            "q": ciudad,
            "appid": API_KEY,
            "units": "metric",
            "lang": "es"
        }, timeout=5)

        data = response.json()
        condicion = data["weather"][0]["main"].lower()

        if condicion in ("rain", "drizzle", "thunderstorm"):
            return "lluvioso"
        elif condicion in ("clouds",):
            return "nublado"
        else:
            return "soleado"

    except Exception:
        return "cualquiera"