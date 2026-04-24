from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Acá definís con qué base de datos trabajás.
# SQLite guarda todo en un archivo local (planify.db) — ideal para empezar.
# Cuando quieras pasar a PostgreSQL, solo cambiás esta línea por:
# DATABASE_URL = "postgresql://usuario:contraseña@localhost/planify"
DATABASE_URL = "sqlite:///./planify.db"

# El "engine" es el motor que conecta Python con la base de datos.
# check_same_thread=False es necesario solo para SQLite con FastAPI.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

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