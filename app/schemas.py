from pydantic import BaseModel, EmailStr
from typing import Optional


# ─────────────────────────────────────────────
# SCHEMAS DE USUARIO
# ─────────────────────────────────────────────

# Lo que el usuario manda al registrarse
class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str


# Lo que devolvemos al consultar un usuario (nunca la contraseña)
class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: str

    class Config:
        from_attributes = True  # Permite leer datos desde objetos SQLAlchemy


# ─────────────────────────────────────────────
# SCHEMAS DE PLAN
# ─────────────────────────────────────────────

# Lo que se manda para crear un plan (desde el admin o seed de datos)
class PlanCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None

    hora_inicio: Optional[int] = None
    hora_fin: Optional[int] = None
    presupuesto_min: float = 0
    presupuesto_max: Optional[float] = None

    personas_min: int = 1
    personas_max: Optional[int] = None

    acepta_mascotas: bool = False
    es_exterior: bool = True

    latitud: Optional[float] = None
    longitud: Optional[float] = None
    direccion: Optional[str] = None

    clima_recomendado: str = "cualquiera"


# Lo que devolvemos al consultar planes
class PlanOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    imagen_url: Optional[str]
    hora_inicio: Optional[int]
    hora_fin: Optional[int]
    presupuesto_min: float
    presupuesto_max: Optional[float]
    personas_min: int
    personas_max: Optional[int]
    acepta_mascotas: bool
    es_exterior: bool
    latitud: Optional[float]
    longitud: Optional[float]
    direccion: Optional[str]
    clima_recomendado: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# SCHEMA DE FILTROS DE BÚSQUEDA
# Lo que el usuario manda para buscar planes.
# Todos son opcionales — el usuario elige cuáles aplicar.
# ─────────────────────────────────────────────
class FiltrosBusqueda(BaseModel):
    hora: Optional[int] = None                  # ej: 15 (3pm)
    presupuesto_max: Optional[float] = None     # ej: 5000
    cantidad_personas: Optional[int] = None     # ej: 4
    acepta_mascotas: Optional[bool] = None      # True / False
    es_exterior: Optional[bool] = None          # True=aire libre
    clima: Optional[str] = None                 # "soleado", "lluvioso", etc.
    lat_usuario: Optional[float] = None         # posición del usuario
    lon_usuario: Optional[float] = None
    km_max: Optional[float] = None              # radio de búsqueda en km


# ─────────────────────────────────────────────
# SCHEMA DE DESCARTE
# ─────────────────────────────────────────────
class DescarteCreate(BaseModel):
    usuario_id: int
    plan_id: int