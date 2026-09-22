from pydantic import BaseModel, ConfigDict, Field


class MedicoBase(BaseModel):
    """
    Datos básicos de un médico.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    especialidad: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Especialidad médica"
    )

    registro_profesional: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Registro profesional del médico"
    )


class MedicoCreate(MedicoBase):
    """
    Datos necesarios para crear el perfil de un médico.
    """

    usuario_id: int = Field(
        ...,
        gt=0,
        description="ID del usuario asociado al médico"
    )


class MedicoUpdate(BaseModel):
    """
    Datos permitidos para actualizar el perfil de un médico.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    especialidad: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
        description="Nueva especialidad médica"
    )

    registro_profesional: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="Nuevo registro profesional"
    )


class MedicoResponse(MedicoBase):
    """
    Información de un médico que puede devolverse mediante la API.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int = Field(
        ...,
        gt=0,
        description="Identificador del médico"
    )

    usuario_id: int = Field(
        ...,
        gt=0,
        description="ID del usuario asociado"
    )
