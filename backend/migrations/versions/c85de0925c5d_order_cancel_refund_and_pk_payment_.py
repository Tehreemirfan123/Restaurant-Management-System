"""order cancel, refund and pk payment methods

Revision ID: c85de0925c5d
Revises: f5601a800b25
Create Date: 2026-09-21 14:13:56.739910

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c85de0925c5d'
down_revision: Union[str, Sequence[str], None] = 'f5601a800b25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add new enum values for cancellation, refunds and PK payment methods."""
    op.execute(
        "ALTER TYPE orderstatusenum ADD VALUE IF NOT EXISTS 'cancelled'"
    )
    op.execute(
        "ALTER TYPE paymentstatusenum ADD VALUE IF NOT EXISTS 'refunded'"
    )
    op.execute(
        "ALTER TYPE paymentmethodenum ADD VALUE IF NOT EXISTS 'jazzcash'"
    )
    op.execute(
        "ALTER TYPE paymentmethodenum ADD VALUE IF NOT EXISTS 'easypaisa'"
    )


def downgrade() -> None:
    """Postgres cannot easily drop individual enum values, so these are
    intentionally left in place."""
    pass
