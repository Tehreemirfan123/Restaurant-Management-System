"""customer segment

Revision ID: 4a01987d5371
Revises: 985c504cd7a8
Create Date: 2026-09-21 13:30:22.030957

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a01987d5371'
down_revision: Union[str, Sequence[str], None] = '985c504cd7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


segment_enum = sa.Enum(
    'office', 'student', 'hostel', 'household', 'other',
    name='customersegmentenum',
)


def upgrade() -> None:
    """Upgrade schema."""
    segment_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'customers',
        sa.Column('segment', segment_enum, nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('customers', 'segment')
    segment_enum.drop(op.get_bind(), checkfirst=True)
