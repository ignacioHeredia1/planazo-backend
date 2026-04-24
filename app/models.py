from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


# ─────────────────────────────────────────────
# TABLA: usuarios
# Guarda cada persona registrada en la app.
# ─────────────────────────────────────────────
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Un usuario puede descartar muchos planes
    descartes = relationship("Descarte", back_populates="usuario")


# ─────────────────────────────────────────────
# TABLA: planes
# El catálogo principal de actividades.
# ─────────────────────────────────────────────
class Plan(Base):
    __tablename__ = "planes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    imagen_url = Column(String)

    # Filtros principales
    hora_inicio = Column(Integer)           # hora del día (0-23)
    hora_fin = Column(Integer)              # hora del día (0-23)
    presupuesto_min = Column(Float, default=0)
    presupuesto_max = Column(Float, nullable=True)  # None = sin límite

    personas_min = Column(Integer, default=1)
    personas_max = Column(Integer, nullable=True)   # None = sin límite

    acepta_mascotas = Column(Boolean, default=False)
    es_exterior = Column(Boolean, default=True)     # True=aire libre, False=cerrado

    # Ubicación
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    direccion = Column(String, nullable=True)

    # Clima recomendado (ej: "soleado", "nublado", "cualquiera")
    clima_recomendado = Column(String, default="cualquiera")

    # Relación con descartes
    descartes = relationship("Descarte", back_populates="plan")


# ─────────────────────────────────────────────
# TABLA: descartes
# Registra qué planes descartó cada usuario.
# Es la tabla clave para el sistema de gustos.
# ─────────────────────────────────────────────
class Descarte(Base):
    __tablename__ = "descartes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("planes.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="descartes")
    plan = relationship("Plan", back_populates="descartes")