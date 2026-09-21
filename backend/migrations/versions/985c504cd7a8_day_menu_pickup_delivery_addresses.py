"""day menu, pickup/delivery, addresses

Revision ID: 985c504cd7a8
Revises: d1ed6246d846
Create Date: 2026-09-21 12:53:28.941942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '985c504cd7a8'
down_revision: Union[str, Sequence[str], None] = 'd1ed6246d846'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


day_of_week_enum = sa.Enum(
    'monday', 'tuesday', 'wednesday', 'thursday',
    'friday', 'saturday', 'sunday',
    name='dayofweekenum',
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    # New enum type for the rotating daily menu.
    day_of_week_enum.create(bind, checkfirst=True)

    # New pickup/delivery values on the existing order-type enum.
    op.execute("ALTER TYPE ordertypeenum ADD VALUE IF NOT EXISTS 'pickup'")
    op.execute("ALTER TYPE ordertypeenum ADD VALUE IF NOT EXISTS 'delivery'")

    op.add_column('customers', sa.Column('address', sa.Text(), nullable=True))
    op.add_column(
        'menu_items',
        sa.Column('day_of_week', day_of_week_enum, nullable=True),
    )
    op.add_column(
        'orders',
        sa.Column(
            'delivery_fee',
            sa.Numeric(precision=10, scale=2),
            nullable=False,
            server_default='0',
        ),
    )
    op.add_column(
        'orders',
        sa.Column('delivery_address', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('orders', 'delivery_address')
    op.drop_column('orders', 'delivery_fee')
    op.drop_column('menu_items', 'day_of_week')
    op.drop_column('customers', 'address')

    day_of_week_enum.drop(op.get_bind(), checkfirst=True)
    # Note: Postgres cannot easily drop individual enum values, so the
    # pickup/delivery values on ordertypeenum are intentionally left in place.
