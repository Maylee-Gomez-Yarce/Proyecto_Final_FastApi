from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.roles import require_paciente
from app.models.paciente import Paciente
from app.models.usuario import Usuario
from app.schemas.paciente import PacienteResponse, PacienteUpdate


router = APIRouter(
    prefix="/pacientes",
    tags=["Patients"],
)


@router.get(
    "/me",
    response_model=PacienteResponse,
    summary="Consultar perfil del paciente",
    description=(
        "Obtiene la información del perfil correspondiente "
        "al paciente autenticado."
    ),
    responses={
        401: {
            "description": "Usuario no autenticado o token inválido"
        },
        403: {
            "description": "El usuario no es un paciente o está inactivo"
        },
        404: {
            "description": "El perfil de paciente no existe"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def obtener_mi_perfil_paciente(
    usuario: Usuario = Depends(require_paciente),
    db: Session = Depends(get_db),
):
    """
    Obtiene el perfil del paciente autenticado.
    """

    paciente = db.query(Paciente).filter(
        Paciente.usuario_id == usuario.id
    ).first()

    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El perfil de paciente no existe.",
        )

    return paciente


@router.put(
    "/me",
    response_model=PacienteResponse,
    summary="Actualizar perfil del paciente",
    description=(
        "Actualiza los datos permitidos del perfil del paciente "
        "autenticado."
    ),
    responses={
        401: {
            "description": "Usuario no autenticado o token inválido"
        },
        403: {
            "description": "El usuario no es un paciente o está inactivo"
        },
        404: {
            "description": "El perfil de paciente no existe"
        },
        422: {
            "description": "Datos de actualización inválidos"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def actualizar_mi_perfil_paciente(
    datos: PacienteUpdate,
    usuario: Usuario = Depends(require_paciente),
    db: Session = Depends(get_db),
):
    """
    Actualiza los datos del paciente autenticado.
    """

    paciente = db.query(Paciente).filter(
        Paciente.usuario_id == usuario.id
    ).first()

    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El perfil de paciente no existe.",
        )

    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Debe proporcionar al menos un dato para actualizar.",
        )

    for campo, valor in cambios.items():
        setattr(paciente, campo, valor)

    db.commit()
    db.refresh(paciente)

    return paciente
