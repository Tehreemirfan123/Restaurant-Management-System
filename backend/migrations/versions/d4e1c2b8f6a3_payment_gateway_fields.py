"""payment gateway fields

Revision ID: d4e1c2b8f6a3
Revises: c3f2a9e4b7d1
Create Date: 2026-09-22 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e1c2b8f6a3'
down_revision: Union[str, Sequence[str], None] = 'c3f2a9e4b7d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'payments',
        sa.Column('transaction_ref', sa.String(length=64), nullable=True),
    )
    op.add_column(
        'payments', sa.Column('gateway', sa.String(length=30), nullable=True)
    )
    op.create_unique_constraint(
        'uq_payments_transaction_ref', 'payments', ['transaction_ref']
    )
    op.create_index(
        'ix_payments_transaction_ref', 'payments', ['transaction_ref']
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_payments_transaction_ref', table_name='payments')
    op.drop_constraint(
        'uq_payments_transaction_ref', 'payments', type_='unique'
    )
    op.drop_column('payments', 'gateway')
    op.drop_column('payments', 'transaction_ref')
