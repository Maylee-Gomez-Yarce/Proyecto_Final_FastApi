from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.roles import require_medico
from app.models.usuario import Usuario
from app.schemas.disponibilidad import (
    DisponibilidadCreate,
    DisponibilidadResponse,
    DisponibilidadUpdate,
)
from app.services.disponibilidad_service import (
    actualizar_disponibilidad,
    crear_disponibilidad,
    eliminar_disponibilidad,
    obtener_disponibilidad,
    obtener_disponibilidades,
    obtener_medico_usuario,
)


router = APIRouter(
    prefix="/disponibilidades",
    tags=["Availability"],
)


# ============================================================
# CREAR DISPONIBILIDAD
# ============================================================

@router.post(
    "",
    response_model=DisponibilidadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear disponibilidad",
    description=(
        "Crea un horario de disponibilidad para el médico "
        "autenticado. El médico no puede crear horarios que "
        "se superpongan con otra disponibilidad activa."
    ),
    responses={
        401: {
            "description": "Usuario no autenticado o token inválido"
        },
        403: {
            "description": "Solo los médicos pueden crear disponibilidades"
        },
        409: {
            "description": (
                "El horario se solapa con otra disponibilidad "
                "o ya existe una disponibilidad idéntica"
            )
        },
        422: {
            "description": "Datos de disponibilidad inválidos"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def crear_mi_disponibilidad(
    datos: DisponibilidadCreate,
    usuario: Usuario = Depends(require_medico),
    db: Session = Depends(get_db),
):
    """
    Crea una disponibilidad para el médico autenticado.

    El medico_id enviado en el cuerpo se valida contra
    el médico asociado al usuario autenticado.
    """

    medico = obtener_medico_usuario(
        db=db,
        usuario_id=usuario.id,
    )

    if datos.medico_id != medico.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "No puede crear una disponibilidad "
                "para otro médico."
            ),
        )

    try:
        return crear_disponibilidad(
            db=db,
            medico_id=medico.id,
            dia_semana=datos.dia_semana,
            hora_inicio=datos.hora_inicio,
            hora_fin=datos.hora_fin,
            is_active=datos.is_active,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Ya existe una disponibilidad con "
                "los mismos datos."
            ),
        )


# ============================================================
# LISTAR DISPONIBILIDADES
# ============================================================

@router.get(
    "",
    response_model=list[DisponibilidadResponse],
    summary="Listar disponibilidades",
    description=(
        "Obtiene todas las disponibilidades del médico "
        "autenticado."
    ),
    responses={
        401: {
            "description": "Usuario no autenticado o token inválido"
        },
        403: {
            "description": (
                "Solo los médicos pueden consultar "
                "disponibilidades"
            )
        },
        404: {
            "description": "El perfil médico no existe"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def listar_mis_disponibilidades(
    usuario: Usuario = Depends(require_medico),
    db: Session = Depends(get_db),
):
    """
    Obtiene todas las disponibilidades del médico autenticado.
    """

    medico = obtener_medico_usuario(
        db=db,
        usuario_id=usuario.id,
    )

    return obtener_disponibilidades(
        db=db,
        medico_id=medico.id,
    )


# ============================================================
# CONSULTAR DISPONIBILIDAD
# ============================================================

@router.get(
    "/{disponibilidad_id}",
    response_model=DisponibilidadResponse,
    summary="Consultar disponibilidad",
    description=(
        "Obtiene una disponibilidad específica que "
        "pertenece al médico autenticado."
    ),
    responses={
        401: {
            "description": "Usuario no autenticado o token inválido"
        },
        403: {
            "description": (
                "Solo los médicos pueden consultar "
                "disponibilidades"
            )
        },
        404: {
            "description": "La disponibilidad no existe"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def obtener_mi_disponibilidad(
    disponibilidad_id: int,
    usuario: Usuario = Depends(require_medico),
    db: Session = Depends(get_db),
):
    """
    Obtiene una disponibilidad perteneciente
    al médico autenticado.
    """

    medico = obtener_medico_usuario(
        db=db,
        usuario_id=usuario.id,
    )

    return obtener_disponibilidad(
        db=db,
        medico_id=medico.id,
        disponibilidad_id=disponibilidad_id,
    )


# ============================================================
# ACTUALIZAR DISPONIBILIDAD
# ============================================================

@router.put(
    "/{disponibilidad_id}",
    response_model=DisponibilidadResponse,
    summary="Actualizar disponibilidad",
    description=(
        "Actualiza una disponibilidad perteneciente al médico "
        "autenticado. Se permite actualizar uno o varios campos "
        "sin necesidad de enviar nuevamente toda la información. "
        "Los cambios no pueden generar horarios superpuestos."
    ),
    responses={
        401: {
            "description": "Usuario no autenticado o token inválido"
        },
        403: {
            "description": (
                "Solo los médicos pueden actualizar "
                "disponibilidades"
            )
        },
        404: {
            "description": "La disponibilidad no existe"
        },
        409: {
            "description": (
                "El nuevo horario se solapa con otra "
                "disponibilidad o ya existe"
            )
        },
        422: {
            "description": "Datos de actualización inválidos"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def actualizar_mi_disponibilidad(
    disponibilidad_id: int,
    datos: DisponibilidadUpdate,
    usuario: Usuario = Depends(require_medico),
    db: Session = Depends(get_db),
):
    """
    Actualiza una disponibilidad perteneciente
    al médico autenticado.

    Solo se envían al servicio los campos realmente
    proporcionados por el cliente.
    """

    medico = obtener_medico_usuario(
        db=db,
        usuario_id=usuario.id,
    )

    cambios = datos.model_dump(
        exclude_unset=True
    )

    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Debe proporcionar al menos un dato "
                "para actualizar."
            ),
        )

    try:
        return actualizar_disponibilidad(
            db=db,
            medico_id=medico.id,
            disponibilidad_id=disponibilidad_id,
            **cambios,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Ya existe una disponibilidad con "
                "los mismos datos."
            ),
        )


# ============================================================
# DESACTIVAR DISPONIBILIDAD
# ============================================================

@router.delete(
    "/{disponibilidad_id}",
    response_model=DisponibilidadResponse,
    summary="Desactivar disponibilidad",
    description=(
        "Desactiva una disponibilidad del médico autenticado. "
        "La información se conserva en la base de datos y "
        "no se elimina físicamente."
    ),
    responses={
        401: {
            "description": "Usuario no autenticado o token inválido"
        },
        403: {
            "description": (
                "Solo los médicos pueden eliminar "
                "disponibilidades"
            )
        },
        404: {
            "description": "La disponibilidad no existe"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def eliminar_mi_disponibilidad(
    disponibilidad_id: int,
    usuario: Usuario = Depends(require_medico),
    db: Session = Depends(get_db),
):
    """
    Desactiva una disponibilidad del médico autenticado.

    No se elimina físicamente de la base de datos.
    """

    medico = obtener_medico_usuario(
        db=db,
        usuario_id=usuario.id,
    )

    return eliminar_disponibilidad(
        db=db,
        medico_id=medico.id,
        disponibilidad_id=disponibilidad_id,
    )