from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.dependencies.roles import require_medico, require_paciente

from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.usuario import Usuario

from app.schemas.cita import (
    CitaCreate,
    CitaResponse,
    CitaUpdate,
)

from app.services.cita_service import (
    cancelar_cita,
    cambiar_estado_cita,
    crear_cita,
    obtener_cita,
    obtener_citas_medico,
    obtener_citas_paciente,
)


router = APIRouter(
    prefix="/citas",
    tags=["Appointments"],
)


# ============================================================
# CREAR CITA
# ============================================================

@router.post(
    "",
    response_model=CitaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cita",
    description=(
        "Permite al paciente autenticado reservar una cita "
        "con un médico. La cita se crea inicialmente en "
        "estado 'pendiente'. El paciente solo puede crear "
        "citas para su propio perfil."
    ),
    responses={
        401: {
            "description": (
                "Usuario no autenticado, token inválido "
                "o token expirado"
            )
        },
        403: {
            "description": (
                "El usuario no es un paciente o intenta "
                "crear una cita para otro paciente"
            )
        },
        404: {
            "description": (
                "El perfil del paciente o el médico "
                "no existe"
            )
        },
        409: {
            "description": (
                "El médico no está disponible, el horario "
                "ya está reservado o existe un conflicto"
            )
        },
        422: {
            "description": (
                "Los datos de la cita son inválidos o "
                "la fecha y hora no son válidas"
            )
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def crear_mi_cita(
    datos: CitaCreate,
    usuario: Usuario = Depends(require_paciente),
    db: Session = Depends(get_db),
):
    """
    Permite al paciente autenticado crear una cita.

    El paciente no puede crear una cita para otro paciente.
    El estado inicial siempre es 'pendiente' y no puede
    ser establecido por el cliente.
    """

    paciente = (
        db.query(Paciente)
        .filter(
            Paciente.usuario_id == usuario.id
        )
        .first()
    )

    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El perfil de paciente no existe.",
        )

    if datos.paciente_id != paciente.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "No puede crear una cita en nombre "
                "de otro paciente."
            ),
        )

    try:
        return crear_cita(
            db=db,
            paciente_id=paciente.id,
            medico_id=datos.medico_id,
            fecha=datos.fecha,
            hora=datos.hora,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No fue posible crear la cita porque "
                "el horario ya está reservado."
            ),
        )


# ============================================================
# CITAS DEL PACIENTE
# ============================================================

@router.get(
    "/mis-citas",
    response_model=list[CitaResponse],
    summary="Consultar mis citas",
    description=(
        "Obtiene únicamente las citas asociadas al paciente "
        "autenticado. No permite consultar las citas de "
        "otros pacientes."
    ),
    responses={
        401: {
            "description": (
                "Usuario no autenticado, token inválido "
                "o token expirado"
            )
        },
        403: {
            "description": (
                "Solo los pacientes pueden consultar "
                "sus propias citas"
            )
        },
        404: {
            "description": "El perfil de paciente no existe"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def listar_mis_citas(
    usuario: Usuario = Depends(require_paciente),
    db: Session = Depends(get_db),
):
    """
    Obtiene únicamente las citas del paciente autenticado.
    """

    paciente = (
        db.query(Paciente)
        .filter(
            Paciente.usuario_id == usuario.id
        )
        .first()
    )

    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El perfil de paciente no existe.",
        )

    return obtener_citas_paciente(
        db=db,
        paciente_id=paciente.id,
    )


# ============================================================
# AGENDA DEL MÉDICO
# ============================================================

@router.get(
    "/agenda",
    response_model=list[CitaResponse],
    summary="Consultar agenda médica",
    description=(
        "Obtiene todas las citas correspondientes al médico "
        "autenticado. Un médico únicamente puede consultar "
        "su propia agenda."
    ),
    responses={
        401: {
            "description": (
                "Usuario no autenticado, token inválido "
                "o token expirado"
            )
        },
        403: {
            "description": (
                "Solo los médicos pueden consultar "
                "su agenda"
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
def listar_mi_agenda(
    usuario: Usuario = Depends(require_medico),
    db: Session = Depends(get_db),
):
    """
    Obtiene todas las citas del médico autenticado.
    """

    medico = (
        db.query(Medico)
        .filter(
            Medico.usuario_id == usuario.id
        )
        .first()
    )

    if medico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El perfil médico no existe.",
        )

    return obtener_citas_medico(
        db=db,
        medico_id=medico.id,
    )


# ============================================================
# OBTENER CITA
# ============================================================

@router.get(
    "/{cita_id}",
    response_model=CitaResponse,
    summary="Consultar una cita",
    description=(
        "Permite consultar una cita específica. "
        "El acceso está restringido al paciente propietario "
        "de la cita o al médico asignado."
    ),
    responses={
        401: {
            "description": (
                "Usuario no autenticado, token inválido "
                "o token expirado"
            )
        },
        403: {
            "description": (
                "El usuario autenticado no es el paciente "
                "propietario ni el médico asignado"
            )
        },
        404: {
            "description": "La cita no existe"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def obtener_mi_cita(
    cita_id: int,
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Permite consultar una cita únicamente si:

    - El usuario es el paciente propietario.
    - El usuario es el médico asignado.
    """

    cita = obtener_cita(
        db=db,
        cita_id=cita_id,
    )

    es_paciente = (
        cita.paciente.usuario_id == usuario.id
    )

    es_medico = (
        cita.medico.usuario_id == usuario.id
    )

    if not es_paciente and not es_medico:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permiso para consultar esta cita.",
        )

    return cita


# ============================================================
# ACTUALIZAR ESTADO DE CITA
# ============================================================

@router.put(
    "/{cita_id}",
    response_model=CitaResponse,
    summary="Actualizar estado de una cita",
    description=(
        "Permite exclusivamente al médico asignado modificar "
        "el estado de una cita. La fecha y la hora no pueden "
        "modificarse. Las transiciones de estado son validadas "
        "según las reglas del sistema."
    ),
    responses={
        401: {
            "description": (
                "Usuario no autenticado, token inválido "
                "o token expirado"
            )
        },
        403: {
            "description": (
                "El usuario no es médico o intenta modificar "
                "una cita asignada a otro médico"
            )
        },
        404: {
            "description": "La cita no existe"
        },
        409: {
            "description": (
                "La transición de estado no está permitida, "
                "la cita ya tiene ese estado o está cancelada"
            )
        },
        422: {
            "description": "El estado enviado no es válido"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def actualizar_cita(
    cita_id: int,
    datos: CitaUpdate,
    usuario: Usuario = Depends(require_medico),
    db: Session = Depends(get_db),
):
    """
    El médico asignado puede cambiar únicamente
    el estado de una cita.

    No se permite modificar la fecha ni la hora.
    """

    cita = obtener_cita(
        db=db,
        cita_id=cita_id,
    )

    if cita.medico.usuario_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "No puede modificar una cita "
                "perteneciente a otro médico."
            ),
        )

    try:
        return cambiar_estado_cita(
            db=db,
            cita_id=cita_id,
            nuevo_estado=datos.estado,
        )

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No fue posible actualizar la cita.",
        )


# ============================================================
# CANCELAR CITA
# ============================================================

@router.delete(
    "/{cita_id}",
    response_model=CitaResponse,
    summary="Cancelar cita",
    description=(
        "Permite al paciente autenticado cancelar una cita "
        "de su propiedad. La cita no se elimina físicamente; "
        "se conserva en la base de datos con estado "
        "'cancelada' para mantener el historial."
    ),
    responses={
        401: {
            "description": (
                "Usuario no autenticado, token inválido "
                "o token expirado"
            )
        },
        403: {
            "description": (
                "El usuario no es paciente o intenta "
                "cancelar la cita de otro paciente"
            )
        },
        404: {
            "description": "La cita no existe"
        },
        409: {
            "description": "La cita ya está cancelada"
        },
        500: {
            "description": "Error interno del servidor"
        },
    },
)
def cancelar_mi_cita(
    cita_id: int,
    usuario: Usuario = Depends(require_paciente),
    db: Session = Depends(get_db),
):
    """
    Permite al paciente cancelar únicamente
    sus propias citas.

    La cancelación se realiza de forma lógica
    para conservar el historial.
    """

    cita = obtener_cita(
        db=db,
        cita_id=cita_id,
    )

    if cita.paciente.usuario_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede cancelar la cita de otro paciente.",
        )

    return cancelar_cita(
        db=db,
        cita_id=cita_id,
    )