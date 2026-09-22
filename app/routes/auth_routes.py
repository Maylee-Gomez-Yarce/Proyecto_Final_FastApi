from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db

from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.usuario import Usuario

from app.schemas.auth import (
    LoginUsuario,
    RegistroUsuario,
    TokenResponse,
)

from app.schemas.usuario import UsuarioResponse

from app.security.security import (
    create_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# REGISTRO
# ============================================================

@router.post(
    "/registro",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario",
    description=(
        "Registra un nuevo usuario como paciente o médico. "
        "El correo electrónico y el documento deben ser únicos. "
        "Los médicos deben proporcionar especialidad y "
        "registro profesional."
    ),
    responses={
        409: {
            "description": (
                "El correo, documento o registro profesional "
                "ya está registrado"
            )
        },
        422: {
            "description": "Datos de registro inválidos"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def registrar_usuario(
    datos: RegistroUsuario,
    db: Session = Depends(get_db),
):
    """
    Registra un nuevo usuario.

    Pacientes:
    - Se crea únicamente su perfil de paciente.

    Médicos:
    - Se crea su perfil médico.
    - Deben proporcionar especialidad.
    - Deben proporcionar registro profesional.
    """

    usuario_email = (
        db.query(Usuario)
        .filter(Usuario.email == str(datos.email))
        .first()
    )

    if usuario_email is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está registrado",
        )

    usuario_documento = (
        db.query(Usuario)
        .filter(Usuario.documento == datos.documento)
        .first()
    )

    if usuario_documento is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El documento ya está registrado",
        )

    nuevo_usuario = Usuario(
        nombre=datos.nombre,
        apellido=datos.apellido,
        email=str(datos.email),
        telefono=datos.telefono,
        documento=datos.documento,
        password_hash=hash_password(datos.password),
        rol=datos.rol,
        is_active=True,
    )

    db.add(nuevo_usuario)

    try:
        db.flush()

        if datos.rol == "paciente":
            perfil = Paciente(
                usuario_id=nuevo_usuario.id
            )

        elif datos.rol == "medico":
            perfil = Medico(
                usuario_id=nuevo_usuario.id,
                especialidad=datos.especialidad,
                registro_profesional=datos.registro_profesional,
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Rol no permitido",
            )

        db.add(perfil)

        db.commit()
        db.refresh(nuevo_usuario)

        return nuevo_usuario

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No fue posible registrar el usuario porque "
                "uno de sus datos únicos ya está registrado"
            ),
        )


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description=(
        "Autentica un usuario mediante correo electrónico "
        "y contraseña y genera un token JWT."
    ),
    responses={
        401: {
            "description": "Credenciales incorrectas"
        },
        403: {
            "description": "Usuario inactivo"
        },
        422: {
            "description": "Datos de inicio de sesión inválidos"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def iniciar_sesion(
    datos: LoginUsuario,
    db: Session = Depends(get_db),
):
    """
    Autentica un usuario y genera un token JWT.
    """

    usuario = (
        db.query(Usuario)
        .filter(Usuario.email == str(datos.email))
        .first()
    )

    if usuario is None or not verify_password(
        datos.password,
        usuario.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está inactivo",
        )

    token = create_access_token(
        {
            "sub": str(usuario.id),
            "rol": usuario.rol,
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        usuario_id=usuario.id,
        rol=usuario.rol,
    )


# ============================================================
# USUARIO AUTENTICADO
# ============================================================

@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Consultar usuario autenticado",
    description=(
        "Devuelve la información del usuario actualmente "
        "autenticado mediante su token JWT."
    ),
    responses={
        401: {
            "description": (
                "Token inválido, expirado o ausente"
            )
        },
        403: {
            "description": "Usuario inactivo"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def obtener_usuario_actual(
    usuario: Usuario = Depends(get_current_user),
):
    """
    Obtiene la información del usuario autenticado.
    """

    return usuario