from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
from passlib.context import CryptContext
import math

from app import models, schemas
from app.database import engine, get_db
from app.clima import obtener_clima_ciudad
from app.ia import generar_planes_ia

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Planazo API", version="1.0")

app.add_middleware(SessionMiddleware, secret_key="clave-super-secreta-planazo-2025")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

ADMIN_USUARIO = "admin"
ADMIN_PASSWORD = "planazo123"
PLANES_MINIMOS = 10

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashear_password(password: str) -> str:
    return pwd_context.hash(password[:72])


def verificar_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password[:72], hashed)


def admin_requerido(request: Request) -> bool:
    return bool(request.session.get("admin_logueado"))


def get_usuario_sesion(request: Request, db: Session) -> Optional[models.Usuario]:
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return None
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()


def get_or_create_usuario_invitado(db: Session):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == 1).first()
    if not usuario:
        usuario = models.Usuario(nombre="invitado", email="invitado@planazo.com", hashed_password="")
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


def parse_int(valor) -> Optional[int]:
    try:
        return int(valor) if valor and str(valor).strip() else None
    except (ValueError, TypeError):
        return None


def parse_float(valor) -> Optional[float]:
    try:
        return float(valor) if valor and str(valor).strip() else None
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
    regenerar: Optional[str] = None,
    db: Session = Depends(get_db)
):
    usuario_sesion = get_usuario_sesion(request, db)
    usuario = usuario_sesion if usuario_sesion else get_or_create_usuario_invitado(db)

    hora_int = parse_int(hora)
    presupuesto_float = parse_float(presupuesto_max)
    personas_int = parse_int(cantidad_personas)
    lat_float = parse_float(lat_usuario)
    lon_float = parse_float(lon_usuario)
    km_float = parse_float(km_max)

    clima_actual = None
    clima_a_filtrar = clima if clima else None
    if ciudad and ciudad.strip():
        clima_actual = obtener_clima_ciudad(ciudad)
        if not clima_a_filtrar:
            clima_a_filtrar = clima_actual

    descartados = db.query(models.Descarte.plan_id).filter(
        models.Descarte.usuario_id == usuario.id
    ).all()
    ids_descartados = [d[0] for d in descartados]

    ids_favoritos = []
    if usuario_sesion:
        favs = db.query(models.Favorito.plan_id).filter(
            models.Favorito.usuario_id == usuario_sesion.id
        ).all()
        ids_favoritos = [f[0] for f in favs]

    query = db.query(models.Plan)
    if ids_descartados:
        query = query.filter(~models.Plan.id.in_(ids_descartados))

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
    elif acepta_mascotas == "false":
        query = query.filter(models.Plan.acepta_mascotas == False)
    if es_exterior == "true":
        query = query.filter(models.Plan.es_exterior == True)
    elif es_exterior == "false":
        query = query.filter(models.Plan.es_exterior == False)
    if clima_a_filtrar:
        query = query.filter(
            (models.Plan.clima_recomendado == "cualquiera") |
            (models.Plan.clima_recomendado == clima_a_filtrar)
        )

    planes_db = query.all()

    if lat_float is not None and lon_float is not None and km_float is not None:
        planes_db = [
            p for p in planes_db
            if p.latitud is None or p.longitud is None or
            distancia_km(lat_float, lon_float, p.latitud, p.longitud) <= km_float
        ]

    planes = [
        {
            "id": p.id,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "hora_inicio": p.hora_inicio,
            "hora_fin": p.hora_fin,
            "presupuesto_min": p.presupuesto_min,
            "presupuesto_max": p.presupuesto_max,
            "personas_min": p.personas_min,
            "personas_max": p.personas_max,
            "acepta_mascotas": p.acepta_mascotas,
            "es_exterior": p.es_exterior,
            "clima_recomendado": p.clima_recomendado,
            "direccion": p.direccion,
            "latitud": p.latitud,
            "longitud": p.longitud,
            "generado_por_ia": False,
        }
        for p in planes_db
    ]

    # Generar planes con IA
    planes_ia = []
    hay_filtros = any([hora_int, presupuesto_float, personas_int, acepta_mascotas, es_exterior, clima_a_filtrar, ciudad])

    if hay_filtros:
        if regenerar == '1':
            cantidad_a_generar = 10
        elif len(planes) < PLANES_MINIMOS:
            cantidad_a_generar = PLANES_MINIMOS - len(planes)
        else:
            cantidad_a_generar = 0

        if cantidad_a_generar > 0:
            planes_ia = generar_planes_ia(
                hora=hora_int,
                presupuesto_max=presupuesto_float,
                cantidad_personas=personas_int,
                acepta_mascotas=acepta_mascotas == "true" if acepta_mascotas else None,
                es_exterior=es_exterior == "true" if es_exterior else None,
                clima=clima_a_filtrar,
                ciudad=ciudad,
                cantidad=cantidad_a_generar
            )

    todos_los_planes = planes + planes_ia
    hay_planes_ia = len(planes_ia) > 0

    planes_con_ubicacion = [
        {"nombre": p["nombre"], "latitud": p["latitud"], "longitud": p["longitud"], "direccion": p.get("direccion")}
        for p in todos_los_planes if p.get("latitud") is not None and p.get("longitud") is not None
    ]

    filtros = {
        "hora": hora_int, "presupuesto_max": presupuesto_float,
        "cantidad_personas": personas_int, "acepta_mascotas": acepta_mascotas,
        "es_exterior": es_exterior, "clima": clima, "ciudad": ciudad,
        "lat_usuario": lat_float, "lon_usuario": lon_float, "km_max": km_float,
    }

    return templates.TemplateResponse(
        request=request, name="index.html",
        context={
            "planes": todos_los_planes,
            "filtros": filtros,
            "clima_actual": clima_actual,
            "planes_con_ubicacion": planes_con_ubicacion,
            "usuario": usuario_sesion,
            "ids_favoritos": ids_favoritos,
            "hay_planes_ia": hay_planes_ia,
        }
    )


# ─────────────────────────────────────────────
# DESCARTAR Y RESTAURAR
# ─────────────────────────────────────────────
@app.post("/descartar/{plan_id}")
def descartar_plan(plan_id: int, request: Request, db: Session = Depends(get_db)):
    usuario_sesion = get_usuario_sesion(request, db)
    usuario = usuario_sesion if usuario_sesion else get_or_create_usuario_invitado(db)
    existente = db.query(models.Descarte).filter(
        models.Descarte.usuario_id == usuario.id,
        models.Descarte.plan_id == plan_id
    ).first()
    if not existente:
        db.add(models.Descarte(usuario_id=usuario.id, plan_id=plan_id))
        db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/restaurar")
def restaurar_todos(request: Request, db: Session = Depends(get_db)):
    usuario_sesion = get_usuario_sesion(request, db)
    usuario = usuario_sesion if usuario_sesion else get_or_create_usuario_invitado(db)
    db.query(models.Descarte).filter(models.Descarte.usuario_id == usuario.id).delete()
    db.commit()
    return RedirectResponse(url="/", status_code=303)


# ─────────────────────────────────────────────
# REGISTRO Y LOGIN DE USUARIOS
# ─────────────────────────────────────────────
@app.get("/registro", response_class=HTMLResponse)
def registro_form(request: Request):
    if request.session.get("usuario_id"):
        return RedirectResponse(url="/perfil", status_code=303)
    return templates.TemplateResponse(request=request, name="registro.html", context={"error": None})


@app.post("/registro")
def registro(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existente = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if existente:
        return templates.TemplateResponse(
            request=request, name="registro.html",
            context={"error": "Ya existe una cuenta con ese email"}
        )
    if len(password) < 6:
        return templates.TemplateResponse(
            request=request, name="registro.html",
            context={"error": "La contraseña debe tener al menos 6 caracteres"}
        )
    nuevo = models.Usuario(nombre=nombre, email=email, hashed_password=hashear_password(password))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    request.session["usuario_id"] = nuevo.id
    return RedirectResponse(url="/perfil", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_usuario_form(request: Request, mensaje: Optional[str] = None):
    if request.session.get("usuario_id"):
        return RedirectResponse(url="/perfil", status_code=303)
    return templates.TemplateResponse(
        request=request, name="login_usuario.html",
        context={"error": None, "mensaje": mensaje}
    )


@app.post("/login")
def login_usuario(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not usuario or not usuario.hashed_password or not verificar_password(password, usuario.hashed_password):
        return templates.TemplateResponse(
            request=request, name="login_usuario.html",
            context={"error": "Email o contraseña incorrectos", "mensaje": None}
        )
    request.session["usuario_id"] = usuario.id
    return RedirectResponse(url="/perfil", status_code=303)


@app.get("/logout")
def logout_usuario(request: Request):
    request.session.pop("usuario_id", None)
    return RedirectResponse(url="/", status_code=303)


# ─────────────────────────────────────────────
# PERFIL Y FAVORITOS
# ─────────────────────────────────────────────
@app.get("/perfil", response_class=HTMLResponse)
def perfil(request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_sesion(request, db)
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)
    favoritos_ids = db.query(models.Favorito.plan_id).filter(
        models.Favorito.usuario_id == usuario.id
    ).all()
    favoritos = [db.query(models.Plan).filter(models.Plan.id == f[0]).first() for f in favoritos_ids]
    return templates.TemplateResponse(
        request=request, name="perfil.html",
        context={"usuario": usuario, "favoritos": [f for f in favoritos if f]}
    )


@app.post("/favoritos/agregar/{plan_id}")
def agregar_favorito(plan_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_sesion(request, db)
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)
    existente = db.query(models.Favorito).filter(
        models.Favorito.usuario_id == usuario.id,
        models.Favorito.plan_id == plan_id
    ).first()
    if not existente:
        db.add(models.Favorito(usuario_id=usuario.id, plan_id=plan_id))
        db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/favoritos/quitar/{plan_id}")
def quitar_favorito(plan_id: int, request: Request, db: Session = Depends(get_db)):
    usuario = get_usuario_sesion(request, db)
    if not usuario:
        return RedirectResponse(url="/login", status_code=303)
    db.query(models.Favorito).filter(
        models.Favorito.usuario_id == usuario.id,
        models.Favorito.plan_id == plan_id
    ).delete()
    db.commit()
    return RedirectResponse(url="/perfil", status_code=303)


# ─────────────────────────────────────────────
# LOGIN ADMIN
# ─────────────────────────────────────────────
@app.get("/admin/login", response_class=HTMLResponse)
def admin_login_form(request: Request):
    if request.session.get("admin_logueado"):
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html", context={"error": None})


@app.post("/admin/login")
def admin_login(request: Request, usuario: str = Form(...), password: str = Form(...)):
    if usuario == ADMIN_USUARIO and password == ADMIN_PASSWORD:
        request.session["admin_logueado"] = True
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(
        request=request, name="login.html",
        context={"error": "Usuario o contraseña incorrectos"}
    )


@app.get("/admin/logout")
def admin_logout(request: Request):
    request.session.pop("admin_logueado", None)
    return RedirectResponse(url="/", status_code=303)


# ─────────────────────────────────────────────
# PANEL ADMIN
# ─────────────────────────────────────────────
@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, mensaje: Optional[str] = None, db: Session = Depends(get_db)):
    if not admin_requerido(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    planes = db.query(models.Plan).all()
    return templates.TemplateResponse(
        request=request, name="admin.html", context={"planes": planes, "mensaje": mensaje}
    )


@app.get("/admin/nuevo", response_class=HTMLResponse)
def admin_nuevo_form(request: Request):
    if not admin_requerido(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    return templates.TemplateResponse(request=request, name="admin_form.html", context={"plan": None})


@app.post("/admin/nuevo")
def admin_crear_plan(
    request: Request,
    nombre: str = Form(...), descripcion: str = Form(""),
    hora_inicio: str = Form(""), hora_fin: str = Form(""),
    presupuesto_min: str = Form("0"), presupuesto_max: str = Form(""),
    personas_min: str = Form("1"), personas_max: str = Form(""),
    acepta_mascotas: str = Form("false"), es_exterior: str = Form("true"),
    clima_recomendado: str = Form("cualquiera"),
    direccion: str = Form(""), latitud: str = Form(""), longitud: str = Form(""),
    db: Session = Depends(get_db)
):
    if not admin_requerido(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    db.add(models.Plan(
        nombre=nombre, descripcion=descripcion or None,
        hora_inicio=parse_int(hora_inicio), hora_fin=parse_int(hora_fin),
        presupuesto_min=parse_float(presupuesto_min) or 0,
        presupuesto_max=parse_float(presupuesto_max),
        personas_min=parse_int(personas_min) or 1,
        personas_max=parse_int(personas_max),
        acepta_mascotas=acepta_mascotas == "true",
        es_exterior=es_exterior == "true",
        clima_recomendado=clima_recomendado,
        direccion=direccion or None,
        latitud=parse_float(latitud), longitud=parse_float(longitud),
    ))
    db.commit()
    return RedirectResponse(url="/admin?mensaje=Plan agregado correctamente", status_code=303)


@app.get("/admin/editar/{plan_id}", response_class=HTMLResponse)
def admin_editar_form(plan_id: int, request: Request, db: Session = Depends(get_db)):
    if not admin_requerido(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        return RedirectResponse(url="/admin", status_code=303)
    return templates.TemplateResponse(request=request, name="admin_form.html", context={"plan": plan})


@app.post("/admin/editar/{plan_id}")
def admin_actualizar_plan(
    plan_id: int, request: Request,
    nombre: str = Form(...), descripcion: str = Form(""),
    hora_inicio: str = Form(""), hora_fin: str = Form(""),
    presupuesto_min: str = Form("0"), presupuesto_max: str = Form(""),
    personas_min: str = Form("1"), personas_max: str = Form(""),
    acepta_mascotas: str = Form("false"), es_exterior: str = Form("true"),
    clima_recomendado: str = Form("cualquiera"),
    direccion: str = Form(""), latitud: str = Form(""), longitud: str = Form(""),
    db: Session = Depends(get_db)
):
    if not admin_requerido(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        return RedirectResponse(url="/admin", status_code=303)
    plan.nombre = nombre
    plan.descripcion = descripcion or None
    plan.hora_inicio = parse_int(hora_inicio)
    plan.hora_fin = parse_int(hora_fin)
    plan.presupuesto_min = parse_float(presupuesto_min) or 0
    plan.presupuesto_max = parse_float(presupuesto_max)
    plan.personas_min = parse_int(personas_min) or 1
    plan.personas_max = parse_int(personas_max)
    plan.acepta_mascotas = acepta_mascotas == "true"
    plan.es_exterior = es_exterior == "true"
    plan.clima_recomendado = clima_recomendado
    plan.direccion = direccion or None
    plan.latitud = parse_float(latitud)
    plan.longitud = parse_float(longitud)
    db.commit()
    return RedirectResponse(url="/admin?mensaje=Plan actualizado correctamente", status_code=303)


@app.post("/admin/eliminar/{plan_id}")
def admin_eliminar_plan(plan_id: int, request: Request, db: Session = Depends(get_db)):
    if not admin_requerido(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if plan:
        db.query(models.Descarte).filter(models.Descarte.plan_id == plan_id).delete()
        db.query(models.Favorito).filter(models.Favorito.plan_id == plan_id).delete()
        db.delete(plan)
        db.commit()
    return RedirectResponse(url="/admin?mensaje=Plan eliminado correctamente", status_code=303)


# ─────────────────────────────────────────────
# API REST
# ─────────────────────────────────────────────
@app.get("/api/planes", response_model=List[schemas.PlanOut])
def api_planes(db: Session = Depends(get_db)):
    return db.query(models.Plan).all()
# ─────────────────────────────────────────────
# DETALLE DE UN PLAN
# ─────────────────────────────────────────────
@app.get("/plan/{plan_id}", response_class=HTMLResponse)
def detalle_plan(plan_id: int, request: Request, db: Session = Depends(get_db)):
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        return RedirectResponse(url="/", status_code=303)
    usuario = get_usuario_sesion(request, db)
    en_favoritos = False
    if usuario:
        en_favoritos = db.query(models.Favorito).filter(
            models.Favorito.usuario_id == usuario.id,
            models.Favorito.plan_id == plan_id
        ).first() is not None
    return templates.TemplateResponse(
        request=request, name="detalle.html",
        context={"plan": plan, "usuario": usuario, "en_favoritos": en_favoritos}
    )