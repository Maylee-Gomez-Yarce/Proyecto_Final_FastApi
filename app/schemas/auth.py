from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


class RegistroUsuario(BaseModel):
    """
    Datos necesarios para registrar un usuario.

    Los pacientes no requieren información profesional.
    Los médicos deben proporcionar especialidad y
    registro profesional.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
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
        description="Correo electrónico válido"
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

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Contraseña del usuario"
    )

    rol: Literal["paciente", "medico"] = Field(
        ...,
        description="Rol del usuario"
    )

    especialidad: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description=(
            "Especialidad médica. Obligatoria cuando "
            "el rol es 'medico'."
        )
    )

    registro_profesional: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        description=(
            "Registro profesional del médico. Obligatorio "
            "cuando el rol es 'medico'."
        )
    )

    @field_validator("nombre", "apellido")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        if not value:
            raise ValueError("Este campo es obligatorio")

        if not all(
            character.isalpha() or character in " -'"
            for character in value
        ):
            raise ValueError(
                "Solo se permiten letras, espacios, "
                "guiones y apóstrofes"
            )

        return value

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError(
                "El teléfono debe contener únicamente números"
            )

        return value

    @field_validator("documento")
    @classmethod
    def validar_documento(cls, value: str) -> str:
        if not value.isalnum():
            raise ValueError(
                "El documento solo puede contener letras y números"
            )

        return value

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str) -> str:
        if any(character.isspace() for character in value):
            raise ValueError(
                "La contraseña no puede contener espacios"
            )

        if not any(character.isupper() for character in value):
            raise ValueError(
                "La contraseña debe contener al menos una letra mayúscula"
            )

        if not any(character.islower() for character in value):
            raise ValueError(
                "La contraseña debe contener al menos una letra minúscula"
            )

        if not any(character.isdigit() for character in value):
            raise ValueError(
                "La contraseña debe contener al menos un número"
            )

        if not any(not character.isalnum() for character in value):
            raise ValueError(
                "La contraseña debe contener al menos un carácter especial"
            )

        return value

    @field_validator("especialidad")
    @classmethod
    def validar_especialidad(cls, value: str | None) -> str | None:
        if value is None:
            return value

        if not all(
            character.isalpha() or character in " -'"
            for character in value
        ):
            raise ValueError(
                "La especialidad solo puede contener letras, "
                "espacios, guiones y apóstrofes"
            )

        return value

    @field_validator("registro_profesional")
    @classmethod
    def validar_registro_profesional(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        if not value.isalnum():
            raise ValueError(
                "El registro profesional solo puede contener "
                "letras y números"
            )

        return value

    @model_validator(mode="after")
    def validar_datos_segun_rol(self):
        if self.rol == "medico":
            if not self.especialidad:
                raise ValueError(
                    "La especialidad es obligatoria "
                    "para los médicos"
                )

            if not self.registro_profesional:
                raise ValueError(
                    "El registro profesional es obligatorio "
                    "para los médicos"
                )

        if self.rol == "paciente":
            if self.especialidad is not None:
                raise ValueError(
                    "La especialidad no corresponde "
                    "a un paciente"
                )

            if self.registro_profesional is not None:
                raise ValueError(
                    "El registro profesional no corresponde "
                    "a un paciente"
                )

        return self


class LoginUsuario(BaseModel):
    """
    Datos necesarios para iniciar sesión.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    email: EmailStr = Field(
        ...,
        description="Correo electrónico registrado"
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Contraseña"
    )


class TokenResponse(BaseModel):
    """
    Respuesta generada después de una autenticación exitosa.
    """

    access_token: str = Field(
        ...,
        description="Token JWT de acceso"
    )

    token_type: Literal["bearer"] = Field(
        default="bearer",
        description="Tipo de autenticación"
    )

    usuario_id: int = Field(
        ...,
        gt=0,
        description="Identificador del usuario autenticado"
    )

    rol: Literal["paciente", "medico"] = Field(
        ...,
        description="Rol del usuario autenticado"
    )