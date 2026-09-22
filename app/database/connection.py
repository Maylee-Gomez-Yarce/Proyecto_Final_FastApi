from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# ==========================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ==========================================

DATABASE_URL = "sqlite:///./citas.db"


# ==========================================
# ENGINE
# ==========================================

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


# ==========================================
# SESSION LOCAL
# ==========================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==========================================
# BASE PARA LOS MODELOS
# ==========================================

class Base(DeclarativeBase):
    pass
