from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    descartes = relationship("Descarte", back_populates="usuario")
    favoritos = relationship("Favorito", back_populates="usuario")


class Plan(Base):
    __tablename__ = "planes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    imagen_url = Column(String)

    hora_inicio = Column(Integer)
    hora_fin = Column(Integer)
    presupuesto_min = Column(Float, default=0)
    presupuesto_max = Column(Float, nullable=True)

    personas_min = Column(Integer, default=1)
    personas_max = Column(Integer, nullable=True)

    acepta_mascotas = Column(Boolean, default=False)
    es_exterior = Column(Boolean, default=True)

    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    direccion = Column(String, nullable=True)

    clima_recomendado = Column(String, default="cualquiera")

    descartes = relationship("Descarte", back_populates="plan")
    favoritos = relationship("Favorito", back_populates="plan")


class Descarte(Base):
    __tablename__ = "descartes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("planes.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="descartes")
    plan = relationship("Plan", back_populates="descartes")


class Favorito(Base):
    __tablename__ = "favoritos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("planes.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="favoritos")
    plan = relationship("Plan", back_populates="favoritos")