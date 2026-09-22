from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.models.usuario import Usuario


if TYPE_CHECKING:
    from app.models.disponibilidad import Disponibilidad
    from app.models.cita import Cita


class Medico(Base):
    __tablename__ = "medicos"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    especialidad: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    registro_profesional: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="medico"
    )

    disponibilidades: Mapped[list["Disponibilidad"]] = relationship(
        "Disponibilidad",
        back_populates="medico",
        cascade="all, delete-orphan"
    )

    citas: Mapped[list["Cita"]] = relationship(
        "Cita",
        back_populates="medico",
        cascade="all, delete-orphan"
    )
