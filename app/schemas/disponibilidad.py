from datetime import time

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DisponibilidadBase(BaseModel):
    """
    Datos básicos de una disponibilidad médica.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    dia_semana: int = Field(
        ...,
        ge=0,
        le=6,
        description="Día de la semana: 0 lunes, 1 martes, ..., 6 domingo"
    )

    hora_inicio: time = Field(
        ...,
        description="Hora de inicio de la disponibilidad"
    )

    hora_fin: time = Field(
        ...,
        description="Hora de finalización de la disponibilidad"
    )

    is_active: bool = Field(
        default=True,
        description="Indica si la disponibilidad está activa"
    )

    @field_validator("hora_fin")
    @classmethod
    def validar_hora_fin(
        cls,
        value: time,
        info
    ) -> time:
        hora_inicio = info.data.get("hora_inicio")

        if hora_inicio is not None and value <= hora_inicio:
            raise ValueError(
                "La hora de fin debe ser posterior a la hora de inicio"
            )

        return value


class DisponibilidadCreate(DisponibilidadBase):
    """
    Datos necesarios para crear una disponibilidad.
    """

    medico_id: int = Field(
        ...,
        gt=0,
        description="ID del médico asociado"
    )


class DisponibilidadUpdate(BaseModel):
    """
    Datos permitidos para actualizar una disponibilidad.

    El estado is_active no se modifica mediante PUT.
    La desactivación se realiza mediante DELETE.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    dia_semana: int | None = Field(
        default=None,
        ge=0,
        le=6,
        description="Nuevo día de la semana"
    )

    hora_inicio: time | None = Field(
        default=None,
        description="Nueva hora de inicio"
    )

    hora_fin: time | None = Field(
        default=None,
        description="Nueva hora de finalización"
    )


class DisponibilidadResponse(DisponibilidadBase):
    """
    Información de una disponibilidad que puede devolverse mediante la API.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int = Field(
        ...,
        gt=0,
        description="Identificador de la disponibilidad"
    )

    medico_id: int = Field(
        ...,
        gt=0,
        description="ID del médico asociado"
    )