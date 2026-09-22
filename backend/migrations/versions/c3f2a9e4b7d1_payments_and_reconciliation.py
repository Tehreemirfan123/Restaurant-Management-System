"""payments, order numbers and reconciliation

Revision ID: c3f2a9e4b7d1
Revises: a1875b380fd0
Create Date: 2026-09-22 15:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c3f2a9e4b7d1'
down_revision: Union[str, Sequence[str], None] = 'a1875b380fd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


order_category = postgresql.ENUM(
    'regular', 'custom', 'subscription', 'large',
    name='ordercategoryenum',
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    order_category.create(bind, checkfirst=True)

    # Orders: human-friendly number + category.
    op.add_column(
        'orders',
        sa.Column(
            'order_number',
            sa.Integer(),
            sa.Identity(start=1001),
            nullable=False,
        ),
    )
    op.create_unique_constraint(
        'uq_orders_order_number', 'orders', ['order_number']
    )
    op.create_index(
        'ix_orders_order_number', 'orders', ['order_number']
    )
    op.add_column(
        'orders',
        sa.Column(
            'category',
            order_category,
            nullable=False,
            server_default='regular',
        ),
    )

    # Payments: allow several per order + reconciliation fields.
    op.drop_constraint('payments_order_id_key', 'payments', type_='unique')
    op.create_index('ix_payments_order_id', 'payments', ['order_id'])
    op.add_column(
        'payments', sa.Column('reference', sa.String(length=120), nullable=True)
    )
    op.add_column('payments', sa.Column('note', sa.Text(), nullable=True))
    op.add_column(
        'payments',
        sa.Column('recorded_by_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        'fk_payments_recorded_by',
        'payments',
        'staff',
        ['recorded_by_id'],
        ['id'],
    )
    op.add_column(
        'payments',
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text('now()'),
        ),
    )

    # Settings: configurable advance rule + payment account details.
    op.add_column(
        'settings',
        sa.Column(
            'advance_payment_percent',
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            server_default='50',
        ),
    )
    op.add_column(
        'settings',
        sa.Column(
            'large_order_threshold',
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default='3000',
        ),
    )
    op.add_column(
        'settings', sa.Column('bank_name', sa.String(length=120), nullable=True)
    )
    op.add_column(
        'settings',
        sa.Column('bank_account_name', sa.String(length=150), nullable=True),
    )
    op.add_column(
        'settings',
        sa.Column('bank_account_number', sa.String(length=60), nullable=True),
    )
    op.add_column(
        'settings',
        sa.Column('jazzcash_number', sa.String(length=30), nullable=True),
    )
    op.add_column(
        'settings',
        sa.Column('easypaisa_number', sa.String(length=30), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('settings', 'easypaisa_number')
    op.drop_column('settings', 'jazzcash_number')
    op.drop_column('settings', 'bank_account_number')
    op.drop_column('settings', 'bank_account_name')
    op.drop_column('settings', 'bank_name')
    op.drop_column('settings', 'large_order_threshold')
    op.drop_column('settings', 'advance_payment_percent')

    op.drop_column('payments', 'created_at')
    op.drop_constraint('fk_payments_recorded_by', 'payments', type_='foreignkey')
    op.drop_column('payments', 'recorded_by_id')
    op.drop_column('payments', 'note')
    op.drop_column('payments', 'reference')
    op.drop_index('ix_payments_order_id', table_name='payments')
    op.create_unique_constraint(
        'payments_order_id_key', 'payments', ['order_id']
    )

    op.drop_column('orders', 'category')
    op.drop_index('ix_orders_order_number', table_name='orders')
    op.drop_constraint('uq_orders_order_number', 'orders', type_='unique')
    op.drop_column('orders', 'order_number')

    order_category.drop(op.get_bind(), checkfirst=True)
