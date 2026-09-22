from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


if TYPE_CHECKING:
    from app.models.paciente import Paciente
    from app.models.medico import Medico


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    apellido: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    telefono: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    documento: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    rol: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    paciente: Mapped["Paciente | None"] = relationship(
        "Paciente",
        back_populates="usuario",
        uselist=False
    )

    medico: Mapped["Medico | None"] = relationship(
        "Medico",
        back_populates="usuario",
        uselist=False
    )

    __table_args__ = (
        CheckConstraint(
            "rol IN ('paciente', 'medico')",
            name="ck_usuario_rol"
        ),
    )