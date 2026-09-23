"""Pure pricing rules, kept dependency-free so any service can import them
without creating a circular dependency between order/payment services.
"""

from decimal import Decimal

from models.models import OrderCategoryEnum, Settings


def compute_advance(
    total: Decimal,
    category: OrderCategoryEnum,
    settings: Settings,
) -> tuple[bool, Decimal]:
    """Whether an advance is required for this order, and how much.

    Custom / subscription / large orders (and any order at or above the
    configured large-order threshold) require an advance. The percentage and
    threshold both live in Settings so the rule can change without code edits.
    """
    total = Decimal(total or 0)
    threshold = settings.large_order_threshold or Decimal("0")
    required = category in (
        OrderCategoryEnum.custom,
        OrderCategoryEnum.subscription,
        OrderCategoryEnum.large,
    ) or (threshold > 0 and total >= threshold)

    if not required:
        return False, Decimal("0")

    percent = settings.advance_payment_percent or Decimal("0")
    amount = (total * percent / Decimal("100")).quantize(Decimal("1"))
    return True, amount
