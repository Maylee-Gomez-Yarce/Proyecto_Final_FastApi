from pydantic import BaseModel, ConfigDict, Field


class PacienteBase(BaseModel):
    """
    Datos básicos de un paciente.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    direccion: str | None = Field(
        default=None,
        min_length=5,
        max_length=255,
        description="Dirección de residencia del paciente"
    )


class PacienteCreate(PacienteBase):
    """
    Datos necesarios para crear el perfil de un paciente.
    """

    usuario_id: int = Field(
        ...,
        gt=0,
        description="ID del usuario asociado al paciente"
    )


class PacienteUpdate(BaseModel):
    """
    Datos permitidos para actualizar el perfil de un paciente.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    direccion: str | None = Field(
        default=None,
        min_length=5,
        max_length=255,
        description="Nueva dirección de residencia"
    )


class PacienteResponse(PacienteBase):
    """
    Información de un paciente que puede devolverse mediante la API.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int = Field(
        ...,
        gt=0,
        description="Identificador del paciente"
    )

    usuario_id: int = Field(
        ...,
        gt=0,
        description="ID del usuario asociado"
    )
