"""
ia.py — Genera planes usando la API de Gemini según los filtros del usuario.
"""

import json
import os
from typing import Optional
from dotenv import load_dotenv
from google import genai
from app.imagenes import obtener_imagen

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generar_planes_ia(
    hora: Optional[int] = None,
    presupuesto_max: Optional[float] = None,
    cantidad_personas: Optional[int] = None,
    acepta_mascotas: Optional[bool] = None,
    es_exterior: Optional[bool] = None,
    clima: Optional[str] = None,
    ciudad: Optional[str] = None,
    cantidad: int = 10
) -> list:
    """
    Genera planes usando Gemini basándose en los filtros del usuario.
    Devuelve una lista de dicts con los datos del plan.
    """

    filtros_texto = []
    if hora is not None:
        filtros_texto.append(f"- Hora aproximada: {hora}:00 hs")
    if presupuesto_max is not None:
        filtros_texto.append(f"- Presupuesto máximo: ${presupuesto_max:.0f}")
    if cantidad_personas is not None:
        filtros_texto.append(f"- Cantidad de personas: {cantidad_personas}")
    if acepta_mascotas is not None:
        filtros_texto.append(f"- {'Con mascotas' if acepta_mascotas else 'Sin mascotas'}")
    if es_exterior is not None:
        filtros_texto.append(f"- Lugar: {'Aire libre / exterior' if es_exterior else 'Cerrado / interior'}")
    if clima is not None:
        filtros_texto.append(f"- Clima: {clima}")
    if ciudad is not None:
        filtros_texto.append(f"- Ciudad o zona: {ciudad}")

    filtros_str = "\n".join(filtros_texto) if filtros_texto else "- Sin filtros específicos (sugerí planes variados)"

    prompt = f"""Sos un asistente experto en recomendar planes y actividades reales en Argentina.

El usuario está buscando planes con estas características:
{filtros_str}

Generá exactamente {cantidad} planes creativos, reales y específicos que se adapten a esos filtros.
Es muy importante que el lugar exista y que proveas coordenadas GPS reales (latitud y longitud).

Respondé ÚNICAMENTE con un JSON válido, sin texto adicional, sin explicaciones, sin markdown.
El JSON debe ser un array con exactamente {cantidad} objetos, cada uno con esta estructura:

[
  {{
    "nombre": "Nombre del lugar o plan",
    "descripcion": "Descripción atractiva de 1-2 oraciones",
    "hora_inicio": 10,
    "hora_fin": 18,
    "presupuesto_min": 0,
    "presupuesto_max": 3000,
    "personas_min": 1,
    "personas_max": 6,
    "acepta_mascotas": false,
    "es_exterior": true,
    "clima_recomendado": "soleado",
    "direccion": "Dirección exacta del lugar real",
    "latitud": -34.6172,
    "longitud": -58.3621
  }}
]

Reglas:
- hora_inicio y hora_fin deben ser números enteros entre 0 y 23
- presupuesto_min y presupuesto_max deben ser números en pesos argentinos
- personas_min y personas_max deben ser números enteros
- acepta_mascotas y es_exterior deben ser true o false
- clima_recomendado debe ser "soleado", "nublado", "lluvioso" o "cualquiera"
- direccion debe ser una ubicación precisa en Argentina
- latitud y longitud deben ser números reales (float) apuntando exactamente al lugar en el mapa
- Los planes deben ser lugares reales, variados y realizables en Argentina
- Adaptá los planes a la ciudad o zona si se especificó"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        respuesta = response.text.strip()

        # Limpiar posibles bloques de código markdown
        if "```" in respuesta:
            partes = respuesta.split("```")
            for parte in partes:
                if parte.startswith("json"):
                    respuesta = parte[4:].strip()
                    break
                elif parte.strip().startswith("["):
                    respuesta = parte.strip()
                    break

        planes = json.loads(respuesta)

        for plan in planes:
            plan["generado_por_ia"] = True
            # Asegurarse de que las coordenadas existan en caso de que la IA no las genere bien
            if "latitud" not in plan or "longitud" not in plan:
                plan["latitud"] = None
                plan["longitud"] = None
            plan["imagen_url"] = obtener_imagen(plan["nombre"])

        return planes

    except Exception as e:
        print(f"Error generando planes con IA: {e}")
        return []