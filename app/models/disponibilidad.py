from datetime import time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.models.medico import Medico


class Disponibilidad(Base):
    __tablename__ = "disponibilidades"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    medico_id: Mapped[int] = mapped_column(
        ForeignKey("medicos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # 0 = lunes, 1 = martes, ..., 6 = domingo
    dia_semana: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    hora_inicio: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    hora_fin: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    medico: Mapped["Medico"] = relationship(
        "Medico",
        back_populates="disponibilidades"
    )

    __table_args__ = (
        CheckConstraint(
            "dia_semana BETWEEN 0 AND 6",
            name="ck_disponibilidad_dia_semana"
        ),
        CheckConstraint(
            "hora_inicio < hora_fin",
            name="ck_disponibilidad_horas"
        ),
        UniqueConstraint(
            "medico_id",
            "dia_semana",
            "hora_inicio",
            "hora_fin",
            name="uq_disponibilidad_medico_horario"
        ),
    )
