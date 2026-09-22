"""permitir reutilizar horarios de citas canceladas

Revision ID: 9b7483b4bfaa
Revises: 13ba56e55f2b
Create Date: 2026-09-21 11:08:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b7483b4bfaa"
down_revision: Union[str, Sequence[str], None] = "13ba56e55f2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Reemplaza las restricciones UNIQUE de citas
    por índices únicos parciales.

    Las citas pendientes y confirmadas bloquean el horario.
    Las citas canceladas no bloquean el horario.
    """

    with op.batch_alter_table("citas") as batch_op:
        batch_op.drop_constraint(
            "uq_cita_medico_fecha_hora",
            type_="unique",
        )

        batch_op.drop_constraint(
            "uq_cita_paciente_fecha_hora",
            type_="unique",
        )

    op.create_index(
        "ix_cita_medico_fecha_hora_activa",
        "citas",
        ["medico_id", "fecha", "hora"],
        unique=True,
        sqlite_where=sa.text(
            "estado != 'cancelada'"
        ),
    )

    op.create_index(
        "ix_cita_paciente_fecha_hora_activa",
        "citas",
        ["paciente_id", "fecha", "hora"],
        unique=True,
        sqlite_where=sa.text(
            "estado != 'cancelada'"
        ),
    )


def downgrade() -> None:
    """
    Revierte los índices parciales y restaura
    las restricciones UNIQUE originales.
    """

    op.drop_index(
        "ix_cita_paciente_fecha_hora_activa",
        table_name="citas",
    )

    op.drop_index(
        "ix_cita_medico_fecha_hora_activa",
        table_name="citas",
    )

    with op.batch_alter_table("citas") as batch_op:
        batch_op.create_unique_constraint(
            "uq_cita_medico_fecha_hora",
            ["medico_id", "fecha", "hora"],
        )

        batch_op.create_unique_constraint(
            "uq_cita_paciente_fecha_hora",
            ["paciente_id", "fecha", "hora"],
        )