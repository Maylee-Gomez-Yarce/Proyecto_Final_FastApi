import os
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from dotenv import load_dotenv


# Cargar variables del archivo .env
load_dotenv()


# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "La variable SECRET_KEY no está configurada en el archivo .env"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Configuración de Argon2
password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Genera un hash seguro de una contraseña utilizando Argon2.
    """
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifica una contraseña contra su hash.
    """
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
) -> str:
    """
    Genera un token JWT con fecha de expiración.
    """
    to_encode = data.copy()

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> dict:
    """
    Decodifica y valida un token JWT.
    """
    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )
