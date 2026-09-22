from datetime import date, datetime, time

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.cita import Cita
from app.models.disponibilidad import Disponibilidad
from app.models.medico import Medico
from app.models.paciente import Paciente
from app.models.usuario import Usuario


ESTADOS_VALIDOS = {
    "pendiente",
    "confirmada",
    "cancelada",
}


def obtener_paciente_usuario(
    db: Session,
    usuario_id: int,
) -> Paciente:
    """
    Obtiene el perfil de paciente asociado
    al usuario autenticado.
    """

    paciente = (
        db.query(Paciente)
        .join(Usuario, Paciente.usuario_id == Usuario.id)
        .filter(
            Paciente.usuario_id == usuario_id,
            Usuario.rol == "paciente",
        )
        .first()
    )

    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El perfil de paciente no existe.",
        )

    return paciente


def obtener_medico(
    db: Session,
    medico_id: int,
) -> Medico:
    """
    Obtiene un perfil médico por su identificador.
    """

    medico = (
        db.query(Medico)
        .join(Usuario, Medico.usuario_id == Usuario.id)
        .filter(
            Medico.id == medico_id,
            Usuario.rol == "medico",
        )
        .first()
    )

    if medico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El médico no existe.",
        )

    return medico


def obtener_paciente(
    db: Session,
    paciente_id: int,
) -> Paciente:
    """
    Obtiene un perfil de paciente por su identificador
    y verifica que corresponda a un usuario con rol paciente.
    """

    paciente = (
        db.query(Paciente)
        .join(Usuario, Paciente.usuario_id == Usuario.id)
        .filter(
            Paciente.id == paciente_id,
            Usuario.rol == "paciente",
        )
        .first()
    )

    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El paciente no existe.",
        )

    return paciente


def validar_medico_activo(
    db: Session,
    medico_id: int,
) -> Medico:
    """
    Verifica que el médico exista, tenga rol médico
    y que su usuario se encuentre activo.

    Esta validación se utiliza específicamente
    antes de permitir una nueva reserva.
    """

    medico = (
        db.query(Medico)
        .join(Usuario, Medico.usuario_id == Usuario.id)
        .filter(
            Medico.id == medico_id,
            Usuario.rol == "medico",
        )
        .first()
    )

    if medico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El médico no existe.",
        )

    if not medico.usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El médico no está disponible actualmente.",
        )

    return medico


def validar_paciente_activo(
    db: Session,
    paciente_id: int,
) -> Paciente:
    """
    Verifica que el paciente exista, tenga rol paciente
    y que su usuario se encuentre activo.
    """

    paciente = (
        db.query(Paciente)
        .join(Usuario, Paciente.usuario_id == Usuario.id)
        .filter(
            Paciente.id == paciente_id,
            Usuario.rol == "paciente",
        )
        .first()
    )

    if paciente is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El paciente no existe.",
        )

    if not paciente.usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El paciente no está activo.",
        )

    return paciente


def validar_fecha_hora_cita(
    fecha: date,
    hora: time,
) -> None:
    """
    Verifica que la cita no esté en el pasado.

    - Una fecha anterior a hoy es inválida.
    - Si la fecha es hoy, la hora también debe ser futura.
    """

    ahora = datetime.now()
    fecha_hora_cita = datetime.combine(fecha, hora)

    if fecha_hora_cita <= ahora:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "La fecha y hora de la cita "
                "no pueden estar en el pasado."
            ),
        )


def validar_disponibilidad_medico(
    db: Session,
    medico_id: int,
    fecha: date,
    hora: time,
) -> None:
    """
    Verifica que el médico tenga una disponibilidad activa
    para el día y hora solicitados.

    La hora de inicio se incluye.
    La hora de finalización se excluye.

    Ejemplo:
    disponibilidad 08:00 - 10:00

    08:00 -> permitido
    09:30 -> permitido
    10:00 -> no permitido
    """

    dia_semana = fecha.weekday()

    disponibilidad = (
        db.query(Disponibilidad)
        .filter(
            Disponibilidad.medico_id == medico_id,
            Disponibilidad.dia_semana == dia_semana,
            Disponibilidad.is_active.is_(True),
            Disponibilidad.hora_inicio <= hora,
            Disponibilidad.hora_fin > hora,
        )
        .first()
    )

    if disponibilidad is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El médico no tiene disponibilidad "
                "para la fecha y hora seleccionadas."
            ),
        )


def validar_doble_reserva(
    db: Session,
    medico_id: int,
    fecha: date,
    hora: time,
    cita_id: int | None = None,
) -> None:
    """
    Impide que un médico tenga más de una cita activa
    en la misma fecha y hora.

    Las citas canceladas no bloquean el horario.
    """

    consulta = (
        db.query(Cita)
        .filter(
            Cita.medico_id == medico_id,
            Cita.fecha == fecha,
            Cita.hora == hora,
            Cita.estado != "cancelada",
        )
    )

    if cita_id is not None:
        consulta = consulta.filter(
            Cita.id != cita_id
        )

    cita_existente = consulta.first()

    if cita_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El médico ya tiene una cita reservada "
                "para esa fecha y hora."
            ),
        )


def validar_cita_paciente(
    db: Session,
    paciente_id: int,
    fecha: date,
    hora: time,
    cita_id: int | None = None,
) -> None:
    """
    Impide que un paciente tenga más de una cita activa
    en la misma fecha y hora.

    Las citas canceladas no bloquean el horario.
    """

    consulta = (
        db.query(Cita)
        .filter(
            Cita.paciente_id == paciente_id,
            Cita.fecha == fecha,
            Cita.hora == hora,
            Cita.estado != "cancelada",
        )
    )

    if cita_id is not None:
        consulta = consulta.filter(
            Cita.id != cita_id
        )

    cita_existente = consulta.first()

    if cita_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "El paciente ya tiene una cita reservada "
                "para esa fecha y hora."
            ),
        )


def crear_cita(
    db: Session,
    paciente_id: int,
    medico_id: int,
    fecha: date,
    hora: time,
) -> Cita:
    """
    Crea una nueva cita.

    Toda cita nueva se crea obligatoriamente
    con estado 'pendiente'.
    """

    validar_fecha_hora_cita(
        fecha=fecha,
        hora=hora,
    )

    paciente = validar_paciente_activo(
        db=db,
        paciente_id=paciente_id,
    )

    medico = validar_medico_activo(
        db=db,
        medico_id=medico_id,
    )

    validar_disponibilidad_medico(
        db=db,
        medico_id=medico.id,
        fecha=fecha,
        hora=hora,
    )

    validar_doble_reserva(
        db=db,
        medico_id=medico.id,
        fecha=fecha,
        hora=hora,
    )

    validar_cita_paciente(
        db=db,
        paciente_id=paciente.id,
        fecha=fecha,
        hora=hora,
    )

    cita = Cita(
        paciente_id=paciente.id,
        medico_id=medico.id,
        fecha=fecha,
        hora=hora,
        estado="pendiente",
    )

    db.add(cita)

    try:
        db.commit()
        db.refresh(cita)

    except Exception:
        db.rollback()
        raise

    return cita


def obtener_cita(
    db: Session,
    cita_id: int,
) -> Cita:
    """
    Obtiene una cita por su identificador.
    """

    cita = (
        db.query(Cita)
        .filter(Cita.id == cita_id)
        .first()
    )

    if cita is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La cita no existe.",
        )

    return cita


def obtener_citas_paciente(
    db: Session,
    paciente_id: int,
) -> list[Cita]:
    """
    Obtiene todas las citas de un paciente,
    incluyendo las canceladas para conservar historial.
    """

    return (
        db.query(Cita)
        .filter(Cita.paciente_id == paciente_id)
        .order_by(
            Cita.fecha,
            Cita.hora,
        )
        .all()
    )


def obtener_citas_medico(
    db: Session,
    medico_id: int,
) -> list[Cita]:
    """
    Obtiene todas las citas de un médico,
    incluyendo las canceladas para conservar historial.
    """

    return (
        db.query(Cita)
        .filter(Cita.medico_id == medico_id)
        .order_by(
            Cita.fecha,
            Cita.hora,
        )
        .all()
    )


def cancelar_cita(
    db: Session,
    cita_id: int,
) -> Cita:
    """
    Cancela una cita conservando su registro
    para mantener el historial.
    """

    cita = obtener_cita(
        db=db,
        cita_id=cita_id,
    )

    if cita.estado == "cancelada":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La cita ya se encuentra cancelada.",
        )

    cita.estado = "cancelada"

    try:
        db.commit()
        db.refresh(cita)

    except Exception:
        db.rollback()
        raise

    return cita


def cambiar_estado_cita(
    db: Session,
    cita_id: int,
    nuevo_estado: str,
) -> Cita:
    """
    Cambia el estado de una cita respetando
    las transiciones permitidas.
    """

    cita = obtener_cita(
        db=db,
        cita_id=cita_id,
    )

    if nuevo_estado not in ESTADOS_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El estado de la cita no es válido.",
        )

    if cita.estado == "cancelada":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Una cita cancelada no puede cambiar "
                "nuevamente de estado."
            ),
        )

    if cita.estado == nuevo_estado:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"La cita ya se encuentra "
                f"en estado '{nuevo_estado}'."
            ),
        )

    transiciones_permitidas = {
        "pendiente": {
            "confirmada",
            "cancelada",
        },
        "confirmada": {
            "cancelada",
        },
    }

    estados_permitidos = transiciones_permitidas.get(
        cita.estado,
        set(),
    )

    if nuevo_estado not in estados_permitidos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"No se permite cambiar una cita de estado "
                f"'{cita.estado}' a '{nuevo_estado}'."
            ),
        )

    cita.estado = nuevo_estado

    try:
        db.commit()
        db.refresh(cita)

    except Exception:
        db.rollback()
        raise

    return cita