from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Proporciona una sesión de base de datos para cada petición.

    La sesión se cierra automáticamente al finalizar la petición,
    incluso si ocurre un error.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
