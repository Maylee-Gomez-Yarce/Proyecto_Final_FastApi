from datetime import date, time, datetime
from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, String, Time

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.models.medico import Medico
from app.models.paciente import Paciente


class Cita(Base):
    __tablename__ = "citas"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    paciente_id: Mapped[int] = mapped_column(
        ForeignKey("pacientes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    medico_id: Mapped[int] = mapped_column(
        ForeignKey("medicos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    fecha: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    hora: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pendiente"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    paciente: Mapped["Paciente"] = relationship(
        "Paciente",
        back_populates="citas"
    )

    medico: Mapped["Medico"] = relationship(
        "Medico",
        back_populates="citas"
    )

    __table_args__ = (
        CheckConstraint(
        "estado IN ('pendiente', 'confirmada', 'cancelada')",
        name="ck_cita_estado"
    ),
    Index(
        "ix_cita_medico_fecha_hora_activa",
        "medico_id",
        "fecha",
        "hora",
        unique=True,
        sqlite_where=estado != "cancelada",
    ),
    Index(
        "ix_cita_paciente_fecha_hora_activa",
        "paciente_id",
        "fecha",
        "hora",
        unique=True,
        sqlite_where=estado != "cancelada",
    ),
)
