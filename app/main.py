from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path

from app import models, schemas
from app.database import engine, get_db
from app.clima import obtener_clima_ciudad

# Crea las tablas si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Planify API", version="1.0")

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
    """Crea el usuario invitado si no existe todavía."""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == 1).first()
    if not usuario:
        usuario = models.Usuario(
            nombre="invitado",
            email="invitado@planify.com",
            hashed_password=""
        )
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
    return usuario


# ─────────────────────────────────────────────
# PÁGINA PRINCIPAL
# ─────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    hora: Optional[int] = None,
    presupuesto_max: Optional[float] = None,
    cantidad_personas: Optional[int] = None,
    acepta_mascotas: Optional[str] = None,
    es_exterior: Optional[str] = None,
    clima: Optional[str] = None,
    ciudad: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Asegurarse de que existe el usuario invitado
    usuario = get_or_create_usuario_invitado(db)

    # Clima automático si se escribió una ciudad
    clima_actual = None
    clima_a_filtrar = clima

    if ciudad:
        clima_actual = obtener_clima_ciudad(ciudad)
        if not clima:
            clima_a_filtrar = clima_actual

    # Query base
    query = db.query(models.Plan)

    # Excluir planes descartados por el usuario invitado
    descartados = db.query(models.Descarte.plan_id).filter(
        models.Descarte.usuario_id == usuario.id
    ).subquery()
    query = query.filter(~models.Plan.id.in_(descartados))

    # Aplicar filtros
    if hora is not None:
        query = query.filter(
            (models.Plan.hora_inicio == None) |
            ((models.Plan.hora_inicio <= hora) & (models.Plan.hora_fin >= hora))
        )

    if presupuesto_max is not None:
        query = query.filter(
            (models.Plan.presupuesto_min == None) |
            (models.Plan.presupuesto_min <= presupuesto_max)
        )

    if cantidad_personas is not None:
        query = query.filter(
            (models.Plan.personas_min == None) |
            (models.Plan.personas_min <= cantidad_personas)
        ).filter(
            (models.Plan.personas_max == None) |
            (models.Plan.personas_max >= cantidad_personas)
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

    filtros = {
        "hora": hora,
        "presupuesto_max": presupuesto_max,
        "cantidad_personas": cantidad_personas,
        "acepta_mascotas": acepta_mascotas,
        "es_exterior": es_exterior,
        "clima": clima,
        "ciudad": ciudad,
    }

    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "planes": planes,
        "filtros": filtros,
        "clima_actual": clima_actual,
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