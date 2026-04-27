from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import math

from app import models, schemas
from app.database import engine, get_db
from app.clima import obtener_clima_ciudad

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Planazo API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


def get_or_create_usuario_invitado(db: Session):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == 1).first()
    if not usuario:
        usuario = models.Usuario(
            nombre="invitado",
            email="invitado@planazo.com",
            hashed_password=""
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
    return usuario


def distancia_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def parse_int(valor: Optional[str]) -> Optional[int]:
    """Convierte string a int, devuelve None si está vacío o no es válido."""
    try:
        return int(valor) if valor and valor.strip() else None
    except (ValueError, TypeError):
        return None


def parse_float(valor: Optional[str]) -> Optional[float]:
    """Convierte string a float, devuelve None si está vacío o no es válido."""
    try:
        return float(valor) if valor and valor.strip() else None
    except (ValueError, TypeError):
        return None


# ─────────────────────────────────────────────
# PÁGINA PRINCIPAL
# ─────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    hora: Optional[str] = None,
    presupuesto_max: Optional[str] = None,
    cantidad_personas: Optional[str] = None,
    acepta_mascotas: Optional[str] = None,
    es_exterior: Optional[str] = None,
    clima: Optional[str] = None,
    ciudad: Optional[str] = None,
    lat_usuario: Optional[str] = None,
    lon_usuario: Optional[str] = None,
    km_max: Optional[str] = None,
    db: Session = Depends(get_db)
):
    usuario = get_or_create_usuario_invitado(db)

    # Convertir parámetros a los tipos correctos
    hora_int = parse_int(hora)
    presupuesto_float = parse_float(presupuesto_max)
    personas_int = parse_int(cantidad_personas)
    lat_float = parse_float(lat_usuario)
    lon_float = parse_float(lon_usuario)
    km_float = parse_float(km_max)

    # Clima automático por ciudad
    clima_actual = None
    clima_a_filtrar = clima if clima else None
    if ciudad and ciudad.strip():
        clima_actual = obtener_clima_ciudad(ciudad)
        if not clima_a_filtrar:
            clima_a_filtrar = clima_actual

    # Excluir planes descartados
    descartados = db.query(models.Descarte.plan_id).filter(
        models.Descarte.usuario_id == usuario.id
    ).all()
    ids_descartados = [d[0] for d in descartados]

    query = db.query(models.Plan)
    if ids_descartados:
        query = query.filter(~models.Plan.id.in_(ids_descartados))

    # Aplicar filtros
    if hora_int is not None:
        query = query.filter(
            (models.Plan.hora_inicio == None) |
            ((models.Plan.hora_inicio <= hora_int) & (models.Plan.hora_fin >= hora_int))
        )

    if presupuesto_float is not None:
        query = query.filter(
            (models.Plan.presupuesto_min == None) |
            (models.Plan.presupuesto_min <= presupuesto_float)
        )

    if personas_int is not None:
        query = query.filter(
            (models.Plan.personas_min == None) |
            (models.Plan.personas_min <= personas_int)
        ).filter(
            (models.Plan.personas_max == None) |
            (models.Plan.personas_max >= personas_int)
        )

    if acepta_mascotas == "true":
        query = query.filter(models.Plan.acepta_mascotas == True)

    if es_exterior == "true":
        query = query.filter(models.Plan.es_exterior == True)
    elif es_exterior == "false":
        query = query.filter(models.Plan.es_exterior == False)

    if clima_a_filtrar:
        query = query.filter(
            (models.Plan.clima_recomendado == "cualquiera") |
            (models.Plan.clima_recomendado == clima_a_filtrar)
        )

    planes = query.all()

    # Filtro por distancia
    if lat_float is not None and lon_float is not None and km_float is not None:
        planes = [
            p for p in planes
            if p.latitud is None or p.longitud is None or
            distancia_km(lat_float, lon_float, p.latitud, p.longitud) <= km_float
        ]

    # Datos para el mapa
    planes_con_ubicacion = [
        {
            "nombre": p.nombre,
            "latitud": p.latitud,
            "longitud": p.longitud,
            "direccion": p.direccion,
        }
        for p in planes if p.latitud is not None and p.longitud is not None
    ]

    filtros = {
        "hora": hora_int,
        "presupuesto_max": presupuesto_float,
        "cantidad_personas": personas_int,
        "acepta_mascotas": acepta_mascotas,
        "es_exterior": es_exterior,
        "clima": clima,
        "ciudad": ciudad,
        "lat_usuario": lat_float,
        "lon_usuario": lon_float,
        "km_max": km_float,
    }

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "planes": planes,
            "filtros": filtros,
            "clima_actual": clima_actual,
            "planes_con_ubicacion": planes_con_ubicacion,
        }
    )


# ─────────────────────────────────────────────
# DESCARTAR UN PLAN
# ─────────────────────────────────────────────
@app.post("/descartar/{plan_id}")
def descartar_plan(plan_id: int, db: Session = Depends(get_db)):
    usuario = get_or_create_usuario_invitado(db)

    existente = db.query(models.Descarte).filter(
        models.Descarte.usuario_id == usuario.id,
        models.Descarte.plan_id == plan_id
    ).first()

    if not existente:
        descarte = models.Descarte(usuario_id=usuario.id, plan_id=plan_id)
        db.add(descarte)
        db.commit()

    return RedirectResponse(url="/", status_code=303)


# ─────────────────────────────────────────────
# RESTAURAR TODOS LOS PLANES DESCARTADOS
# ─────────────────────────────────────────────
@app.post("/restaurar")
def restaurar_todos(db: Session = Depends(get_db)):
    usuario = get_or_create_usuario_invitado(db)
    db.query(models.Descarte).filter(
        models.Descarte.usuario_id == usuario.id
    ).delete()
    db.commit()
    return RedirectResponse(url="/", status_code=303)


# ─────────────────────────────────────────────
# API REST
# ─────────────────────────────────────────────
@app.get("/api/planes", response_model=List[schemas.PlanOut])
def api_planes(db: Session = Depends(get_db)):
    return db.query(models.Plan).all()

@app.post("/api/planes", response_model=schemas.PlanOut)
def api_crear_plan(plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    nuevo = models.Plan(**plan.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo