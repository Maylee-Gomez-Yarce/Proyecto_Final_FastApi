from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UsuarioResponse(BaseModel):
    """
    Información pública de un usuario.
    Nunca incluye la contraseña ni su hash.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int = Field(
        ...,
        gt=0,
        description="Identificador único del usuario"
    )

    nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre del usuario"
    )

    apellido: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Apellido del usuario"
    )

    email: EmailStr = Field(
        ...,
        description="Correo electrónico del usuario"
    )

    telefono: str = Field(
        ...,
        min_length=7,
        max_length=20,
        description="Número telefónico"
    )

    documento: str = Field(
        ...,
        min_length=5,
        max_length=30,
        description="Número de documento"
    )

    rol: Literal["paciente", "medico"] = Field(
        ...,
        description="Rol del usuario"
    )

    is_active: bool = Field(
        ...,
        description="Indica si el usuario está activo"
    )


class UsuarioUpdate(BaseModel):
    """
    Datos permitidos para actualizar el perfil de un usuario.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    nombre: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Nuevo nombre"
    )

    apellido: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Nuevo apellido"
    )

    telefono: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
        description="Nuevo número telefónico"
    )

    @field_validator("nombre", "apellido")
    @classmethod
    def validar_nombre(cls, value: str | None) -> str | None:
        if value is None:
            return value

        if not all(
            character.isalpha() or character in " -'"
            for character in value
        ):
            raise ValueError(
                "Solo se permiten letras, espacios, guiones y apóstrofes"
            )

        return value

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, value: str | None) -> str | None:
        if value is None:
            return value

        if not value.isdigit():
            raise ValueError(
                "El teléfono debe contener únicamente números"
            )

        return value
