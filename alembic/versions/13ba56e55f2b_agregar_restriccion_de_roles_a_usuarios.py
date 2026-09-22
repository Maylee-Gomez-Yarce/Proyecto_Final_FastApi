"""agregar restriccion de roles a usuarios

Revision ID: 13ba56e55f2b
Revises: 029d6f43f577
Create Date: 2026-09-21 10:51:09.573502

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "13ba56e55f2b"
down_revision: Union[str, Sequence[str], None] = "029d6f43f577"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agrega la restricción de roles permitidos."""

    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.create_check_constraint(
            "ck_usuario_rol",
            "rol IN ('paciente', 'medico')",
        )


def downgrade() -> None:
    """Elimina la restricción de roles permitidos."""

    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.drop_constraint(
            "ck_usuario_rol",
            type_="check",
        )