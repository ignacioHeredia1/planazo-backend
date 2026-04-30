import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Plan

engine = create_engine("sqlite:///planify.db")
Session = sessionmaker(bind=engine)
session = Session()

planes = session.query(Plan).all()

for plan in planes:
    texto = f"{plan.nombre} {plan.descripcion}".lower()
    
    cat = "relax" # por defecto
    
    if any(palabra in texto for palabra in ["escape", "aventura", "adrenalina", "montaña"]):
        cat = "aventura"
    elif any(palabra in texto for palabra in ["picnic", "parque", "familia", "niños", "zoo", "plaza"]):
        cat = "familiar"
    elif any(palabra in texto for palabra in ["cine", "teatro", "museo", "cultura", "arte", "historia"]):
        cat = "cultural"
    elif any(palabra in texto for palabra in ["comida", "cena", "restaurante", "gastronomia", "merienda", "pizza", "hamburguesa", "asado"]):
        cat = "gastronomia"
    elif any(palabra in texto for palabra in ["pareja", "romantico", "novio", "cita", "vela"]):
        cat = "romantico"
    elif any(palabra in texto for palabra in ["bici", "correr", "futbol", "deporte", "ejercicio", "gimnasio", "entrenar"]):
        cat = "deportivo"
    elif any(palabra in texto for palabra in ["bar", "cerveza", "noche", "boliche", "tragos", "pub"]):
        cat = "nocturno"
    elif any(palabra in texto for palabra in ["spa", "masaje", "relax", "yoga", "meditar", "tranquilo"]):
        cat = "relax"
        
    plan.categoria = cat
    print(f"[{cat.upper()}] {plan.nombre}")

session.commit()
print("Categorias actualizadas!")
