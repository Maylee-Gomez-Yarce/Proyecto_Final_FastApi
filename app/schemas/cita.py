from datetime import date, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


EstadoCita = Literal[
    "pendiente",
    "confirmada",
    "cancelada",
]


class CitaBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    fecha: date = Field(
        ...,
        description="Fecha de la cita en formato YYYY-MM-DD",
    )

    hora: time = Field(
        ...,
        description="Hora de la cita en formato HH:MM",
    )

    @field_validator("fecha")
    @classmethod
    def validar_fecha(
        cls,
        value: date,
    ) -> date:
        hoy = date.today()

        if value < hoy:
            raise ValueError(
                "La fecha de la cita no puede estar en el pasado"
            )

        return value


class CitaCreate(CitaBase):
    """
    Datos permitidos para solicitar una nueva cita.

    El estado no puede ser enviado por el cliente.
    Toda cita nueva se crea automáticamente como
    'pendiente'.
    """

    paciente_id: int = Field(
        ...,
        gt=0,
        description="ID del paciente",
    )

    medico_id: int = Field(
        ...,
        gt=0,
        description="ID del médico",
    )


class CitaUpdate(BaseModel):
    """
    Actualización administrativa de una cita.

    La fecha y la hora no pueden modificarse.
    La única propiedad modificable mediante este esquema
    es el estado.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    estado: EstadoCita = Field(
        ...,
        description=(
            "Nuevo estado de la cita. "
            "Transiciones permitidas: "
            "pendiente → confirmada/cancelada; "
            "confirmada → cancelada."
        ),
    )


class CitaResponse(CitaBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int = Field(
        ...,
        gt=0,
        description="Identificador de la cita",
    )

    paciente_id: int = Field(
        ...,
        gt=0,
        description="ID del paciente",
    )

    medico_id: int = Field(
        ...,
        gt=0,
        description="ID del médico",
    )

    estado: EstadoCita = Field(
        ...,
        description="Estado actual de la cita",
    )