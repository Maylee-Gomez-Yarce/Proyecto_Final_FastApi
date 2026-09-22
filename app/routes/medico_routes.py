from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.roles import require_medico
from app.models.medico import Medico
from app.models.usuario import Usuario
from app.schemas.medico import MedicoResponse, MedicoUpdate


router = APIRouter(
    prefix="/medicos",
    tags=["Doctors"],
)


@router.get(
    "/me",
    response_model=MedicoResponse,
    summary="Consultar perfil médico",
    description=(
        "Obtiene la información profesional correspondiente "
        "al médico autenticado."
    ),
    responses={
        401: {
            "description": "Usuario no autenticado o token inválido"
        },
        403: {
            "description": "El usuario no es un médico o está inactivo"
        },
        404: {
            "description": "El perfil médico no existe"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def obtener_mi_perfil_medico(
    usuario: Usuario = Depends(require_medico),
    db: Session = Depends(get_db),
):
    """
    Obtiene el perfil profesional del médico autenticado.
    """

    medico = db.query(Medico).filter(
        Medico.usuario_id == usuario.id
    ).first()

    if medico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El perfil médico no existe.",
        )

    return medico


@router.put(
    "/me",
    response_model=MedicoResponse,
    summary="Actualizar perfil médico",
    description=(
        "Actualiza los datos profesionales permitidos del médico "
        "autenticado. El registro profesional debe ser único."
    ),
    responses={
        401: {
            "description": "Usuario no autenticado o token inválido"
        },
        403: {
            "description": "El usuario no es un médico o está inactivo"
        },
        404: {
            "description": "El perfil médico no existe"
        },
        409: {
            "description": "El registro profesional ya está registrado"
        },
        422: {
            "description": "Datos de actualización inválidos"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def actualizar_mi_perfil_medico(
    datos: MedicoUpdate,
    usuario: Usuario = Depends(require_medico),
    db: Session = Depends(get_db),
):
    """
    Actualiza los datos profesionales del médico autenticado.
    """

    medico = db.query(Medico).filter(
        Medico.usuario_id == usuario.id
    ).first()

    if medico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El perfil médico no existe.",
        )

    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Debe proporcionar al menos un dato para actualizar.",
        )

    # Verificar que el registro profesional no pertenezca
    # a otro médico.
    nuevo_registro = cambios.get("registro_profesional")

    if nuevo_registro is not None:
        registro_existente = db.query(Medico).filter(
            Medico.registro_profesional == nuevo_registro,
            Medico.id != medico.id,
        ).first()

        if registro_existente is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El registro profesional ya está registrado.",
            )

    for campo, valor in cambios.items():
        setattr(medico, campo, valor)

    db.commit()
    db.refresh(medico)

    return medico