from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.models.usuario import Usuario


if TYPE_CHECKING:
    from app.models.cita import Cita


class Paciente(Base):
    __tablename__ = "pacientes"

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

    direccion: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="paciente"
    )

    citas: Mapped[list["Cita"]] = relationship(
        "Cita",
        back_populates="paciente",
        cascade="all, delete-orphan"
    )
