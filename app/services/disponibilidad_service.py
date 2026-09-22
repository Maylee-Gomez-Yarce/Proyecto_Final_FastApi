from datetime import time

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.disponibilidad import Disponibilidad
from app.models.medico import Medico
from app.models.usuario import Usuario


def obtener_medico_usuario(
    db: Session,
    usuario_id: int,
) -> Medico:
    """
    Obtiene el perfil médico asociado al usuario autenticado.

    También verifica que el usuario tenga rol médico
    y se encuentre activo.
    """

    medico = (
        db.query(Medico)
        .join(Usuario, Medico.usuario_id == Usuario.id)
        .filter(
            Medico.usuario_id == usuario_id,
            Usuario.rol == "medico",
        )
        .first()
    )

    if medico is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El perfil médico no existe.",
        )

    if not medico.usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario médico se encuentra inactivo.",
        )

    return medico


def validar_solapamiento(
    db: Session,
    medico_id: int,
    dia_semana: int,
    hora_inicio: time,
    hora_fin: time,
    disponibilidad_id: int | None = None,
) -> None:
    """
    Verifica que el nuevo horario no se cruce con otro
    horario activo del mismo médico y día.

    Dos rangos se consideran solapados cuando:

        inicio_nuevo < fin_existente
        y
        fin_nuevo > inicio_existente

    Esto permite horarios consecutivos:

        08:00 - 10:00
        10:00 - 12:00

    pero impide:

        08:00 - 10:00
        09:00 - 11:00
    """

    consulta = (
        db.query(Disponibilidad)
        .filter(
            Disponibilidad.medico_id == medico_id,
            Disponibilidad.dia_semana == dia_semana,
            Disponibilidad.is_active.is_(True),
            Disponibilidad.hora_inicio < hora_fin,
            Disponibilidad.hora_fin > hora_inicio,
        )
    )

    if disponibilidad_id is not None:
        consulta = consulta.filter(
            Disponibilidad.id != disponibilidad_id
        )

    existente = consulta.first()

    if existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "La disponibilidad se solapa con otro "
                "horario activo del médico."
            ),
        )


def crear_disponibilidad(
    db: Session,
    medico_id: int,
    dia_semana: int,
    hora_inicio: time,
    hora_fin: time,
    is_active: bool = True,
) -> Disponibilidad:
    """
    Crea una disponibilidad después de validar
    las reglas de negocio.
    """

    if dia_semana < 0 or dia_semana > 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "El día de la semana debe estar "
                "entre 0 y 6."
            ),
        )

    if hora_fin <= hora_inicio:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "La hora de fin debe ser posterior "
                "a la hora de inicio."
            ),
        )

    if is_active:
        validar_solapamiento(
            db=db,
            medico_id=medico_id,
            dia_semana=dia_semana,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
        )

    disponibilidad = Disponibilidad(
        medico_id=medico_id,
        dia_semana=dia_semana,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        is_active=is_active,
    )

    db.add(disponibilidad)

    try:
        db.commit()
        db.refresh(disponibilidad)

    except Exception:
        db.rollback()
        raise

    return disponibilidad


def obtener_disponibilidades(
    db: Session,
    medico_id: int,
) -> list[Disponibilidad]:
    """
    Obtiene todas las disponibilidades del médico,
    incluyendo las inactivas para conservar historial.
    """

    return (
        db.query(Disponibilidad)
        .filter(
            Disponibilidad.medico_id == medico_id
        )
        .order_by(
            Disponibilidad.dia_semana,
            Disponibilidad.hora_inicio,
        )
        .all()
    )


def obtener_disponibilidad(
    db: Session,
    medico_id: int,
    disponibilidad_id: int,
) -> Disponibilidad:
    """
    Obtiene una disponibilidad verificando que
    pertenezca al médico autenticado.
    """

    disponibilidad = (
        db.query(Disponibilidad)
        .filter(
            Disponibilidad.id == disponibilidad_id,
            Disponibilidad.medico_id == medico_id,
        )
        .first()
    )

    if disponibilidad is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La disponibilidad no existe.",
        )

    return disponibilidad


def actualizar_disponibilidad(
    db: Session,
    medico_id: int,
    disponibilidad_id: int,
    dia_semana: int | None = None,
    hora_inicio: time | None = None,
    hora_fin: time | None = None,
    is_active: bool | None = None,
) -> Disponibilidad:
    """
    Actualiza una disponibilidad verificando
    solapamientos y pertenencia al médico.
    """

    disponibilidad = obtener_disponibilidad(
        db=db,
        medico_id=medico_id,
        disponibilidad_id=disponibilidad_id,
    )

    nuevo_dia = (
        dia_semana
        if dia_semana is not None
        else disponibilidad.dia_semana
    )

    nueva_hora_inicio = (
        hora_inicio
        if hora_inicio is not None
        else disponibilidad.hora_inicio
    )

    nueva_hora_fin = (
        hora_fin
        if hora_fin is not None
        else disponibilidad.hora_fin
    )

    nuevo_estado = (
        is_active
        if is_active is not None
        else disponibilidad.is_active
    )

    if nuevo_dia < 0 or nuevo_dia > 6:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "El día de la semana debe estar "
                "entre 0 y 6."
            ),
        )

    if nueva_hora_fin <= nueva_hora_inicio:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "La hora de fin debe ser posterior "
                "a la hora de inicio."
            ),
        )

    if nuevo_estado:
        validar_solapamiento(
            db=db,
            medico_id=medico_id,
            dia_semana=nuevo_dia,
            hora_inicio=nueva_hora_inicio,
            hora_fin=nueva_hora_fin,
            disponibilidad_id=disponibilidad.id,
        )

    disponibilidad.dia_semana = nuevo_dia
    disponibilidad.hora_inicio = nueva_hora_inicio
    disponibilidad.hora_fin = nueva_hora_fin
    disponibilidad.is_active = nuevo_estado

    try:
        db.commit()
        db.refresh(disponibilidad)

    except Exception:
        db.rollback()
        raise

    return disponibilidad


def eliminar_disponibilidad(
    db: Session,
    medico_id: int,
    disponibilidad_id: int,
) -> Disponibilidad:
    """
    Desactiva una disponibilidad.

    Se conserva el registro para mantener historial.
    """

    disponibilidad = obtener_disponibilidad(
        db=db,
        medico_id=medico_id,
        disponibilidad_id=disponibilidad_id,
    )

    if not disponibilidad.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La disponibilidad ya se encuentra inactiva.",
        )

    disponibilidad.is_active = False

    try:
        db.commit()
        db.refresh(disponibilidad)

    except Exception:
        db.rollback()
        raise

    return disponibilidad