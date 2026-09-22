from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.models.usuario import Usuario
from app.security.security import decode_access_token


# Esquema Bearer utilizado por Swagger y FastAPI
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Obtiene el usuario autenticado a partir del token JWT.
    """

    token = credentials.credentials

    # Validar y decodificar el JWT
    try:
        payload = decode_access_token(token)

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtener el identificador del usuario desde 'sub'
    subject = payload.get("sub")

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token no contiene un usuario válido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convertir el identificador a entero
    try:
        usuario_id = int(subject)

    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El identificador del usuario no es válido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buscar el usuario en la base de datos
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El usuario no existe",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que la cuenta esté activa
    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está inactivo",
        )

    return usuario
