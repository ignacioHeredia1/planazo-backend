"""
seed.py — Carga planes de prueba en la base de datos.
Ejecutar con: python seed.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)

planes_prueba = [
    {
        "nombre": "Picnic en el parque",
        "descripcion": "Llevá una manta, algo rico para comer y disfrutá al aire libre.",
        "hora_inicio": 10,
        "hora_fin": 18,
        "presupuesto_min": 0,
        "presupuesto_max": 3000,
        "personas_min": 1,
        "personas_max": 10,
        "acepta_mascotas": True,
        "es_exterior": True,
        "clima_recomendado": "soleado",
        "latitud": -34.6037,
        "longitud": -58.3816,
        "direccion": "Parque Centenario, CABA",
    },
    {
        "nombre": "Escape room",
        "descripcion": "Resolvé acertijos y escapá de la sala con tu grupo.",
        "hora_inicio": 12,
        "hora_fin": 23,
        "presupuesto_min": 3000,
        "presupuesto_max": 8000,
        "personas_min": 2,
        "personas_max": 6,
        "acepta_mascotas": False,
        "es_exterior": False,
        "clima_recomendado": "cualquiera",
        "latitud": -34.5995,
        "longitud": -58.3744,
        "direccion": "Palermo, CABA",
    },
    {
        "nombre": "Noche de juegos de mesa",
        "descripcion": "Catan, Uno, Truco o lo que tengas. Plan perfecto para cualquier clima.",
        "hora_inicio": 18,
        "hora_fin": 23,
        "presupuesto_min": 0,
        "presupuesto_max": 1000,
        "personas_min": 2,
        "personas_max": 8,
        "acepta_mascotas": True,
        "es_exterior": False,
        "clima_recomendado": "cualquiera",
        "latitud": None,
        "longitud": None,
        "direccion": "En casa",
    },
    {
        "nombre": "Senderismo en las sierras",
        "descripcion": "Caminata por senderos naturales con vistas increíbles.",
        "hora_inicio": 7,
        "hora_fin": 16,
        "presupuesto_min": 0,
        "presupuesto_max": 2000,
        "personas_min": 1,
        "personas_max": 15,
        "acepta_mascotas": True,
        "es_exterior": True,
        "clima_recomendado": "soleado",
        "latitud": -31.4135,
        "longitud": -64.1817,
        "direccion": "Sierras de Córdoba",
    },
    {
        "nombre": "Cine",
        "descripcion": "Elegí una película y disfrutá en pantalla grande.",
        "hora_inicio": 12,
        "hora_fin": 23,
        "presupuesto_min": 2000,
        "presupuesto_max": 6000,
        "personas_min": 1,
        "personas_max": 6,
        "acepta_mascotas": False,
        "es_exterior": False,
        "clima_recomendado": "cualquiera",
        "latitud": -34.5881,
        "longitud": -58.4269,
        "direccion": "Alto Palermo, CABA",
    },
    {
        "nombre": "Asado en casa",
        "descripcion": "Nada mejor que un buen asado con amigos.",
        "hora_inicio": 12,
        "hora_fin": 22,
        "presupuesto_min": 2000,
        "presupuesto_max": 10000,
        "personas_min": 3,
        "personas_max": 20,
        "acepta_mascotas": True,
        "es_exterior": True,
        "clima_recomendado": "soleado",
        "latitud": None,
        "longitud": None,
        "direccion": "En casa",
    },
    {
        "nombre": "Visita a un museo",
        "descripcion": "Cultura y entretenimiento para toda la familia.",
        "hora_inicio": 10,
        "hora_fin": 18,
        "presupuesto_min": 0,
        "presupuesto_max": 2000,
        "personas_min": 1,
        "personas_max": 10,
        "acepta_mascotas": False,
        "es_exterior": False,
        "clima_recomendado": "cualquiera",
        "latitud": -34.6158,
        "longitud": -58.3731,
        "direccion": "MALBA, Av. Figueroa Alcorta 3415, CABA",
    },
    {
        "nombre": "Kayak en el río",
        "descripcion": "Aventura acuática para los que buscan adrenalina.",
        "hora_inicio": 9,
        "hora_fin": 17,
        "presupuesto_min": 3000,
        "presupuesto_max": 7000,
        "personas_min": 1,
        "personas_max": 8,
        "acepta_mascotas": False,
        "es_exterior": True,
        "clima_recomendado": "soleado",
        "latitud": -34.4500,
        "longitud": -58.6800,
        "direccion": "Tigre, Buenos Aires",
    },
]


def cargar_datos():
    db = SessionLocal()
    try:
        cantidad = db.query(models.Plan).count()
        if cantidad > 0:
            print(f"La base de datos ya tiene {cantidad} planes. No se cargaron duplicados.")
            return

        for datos in planes_prueba:
            plan = models.Plan(**datos)
            db.add(plan)

        db.commit()
        print(f"✅ Se cargaron {len(planes_prueba)} planes de prueba correctamente.")
    finally:
        db.close()


if __name__ == "__main__":
    cargar_datos()