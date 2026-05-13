import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# En producción (Render), se usa la variable de entorno DATABASE_URL con PostgreSQL.
# En local, se usa SQLite para simplicidad.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./planify.db")

# Render provee URLs con prefijo "postgres://" pero SQLAlchemy necesita "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configuración del engine según el tipo de base de datos
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# SessionLocal es la "sesión" de base de datos.
# Cada request HTTP va a abrir una sesión y cerrarla al terminar.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base es la clase de la que van a heredar todos tus modelos (tablas).
Base = declarative_base()


# Esta función se usa en cada endpoint para obtener y cerrar la sesión.
# FastAPI la llama automáticamente gracias al sistema de "dependencias".
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()