from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db

from app.models.usuario import Usuario

from app.schemas.usuario import (
    UsuarioResponse,
    UsuarioUpdate,
)


router = APIRouter(
    prefix="/usuarios",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Consultar perfil de usuario",
    description=(
        "Obtiene la información del usuario actualmente "
        "autenticado mediante su token JWT. "
        "Cada usuario únicamente puede consultar su propio perfil."
    ),
    responses={
        401: {
            "description": (
                "Usuario no autenticado, token inválido "
                "o token expirado"
            )
        },
        403: {
            "description": "El usuario se encuentra inactivo"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def obtener_mi_perfil(
    usuario: Usuario = Depends(get_current_user),
):
    """
    Obtiene el perfil del usuario autenticado.
    """

    return usuario


@router.put(
    "/me",
    response_model=UsuarioResponse,
    summary="Actualizar perfil de usuario",
    description=(
        "Actualiza los datos personales permitidos del usuario "
        "autenticado. Por seguridad, los campos protegidos como "
        "correo electrónico, documento, contraseña y rol no "
        "pueden modificarse mediante este endpoint."
    ),
    responses={
        401: {
            "description": (
                "Usuario no autenticado, token inválido "
                "o token expirado"
            )
        },
        403: {
            "description": "El usuario se encuentra inactivo"
        },
        422: {
            "description": (
                "Los datos enviados no son válidos "
                "o no se proporcionó ningún campo para actualizar"
            )
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def actualizar_mi_perfil(
    datos: UsuarioUpdate,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Actualiza los datos personales permitidos
    del usuario autenticado.
    """

    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Debe proporcionar al menos un dato "
                "para actualizar."
            ),
        )

    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)

    return usuario