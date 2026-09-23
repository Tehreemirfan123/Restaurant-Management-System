"""Model package.

Models are split into domain modules (enums, staff, menu, order, payment,
customer, table, inventory, settings). Everything is re-exported here so that
both ``from models import X`` and ``from models.models import X`` keep working.
Importing this package registers every ORM class on the shared Base registry,
which is what lets the string-based relationships resolve.
"""

from models.enums import (
    CategoryEnum,
    CustomerSegmentEnum,
    DayOfWeekEnum,
    OrderCategoryEnum,
    OrderStatusEnum,
    OrderTypeEnum,
    PaymentMethodEnum,
    PaymentStatusEnum,
    RoleEnum,
    TableStatusEnum,
)
from models.staff import Staff
from models.menu import MenuItem
from models.order import Order, OrderFeedback, OrderItem
from models.payment import Payment
from models.customer import Customer
from models.table import Table
from models.inventory import InventoryItem, Recipe, RecipeIngredient, WasteLog
from models.settings import Settings

__all__ = [
    # enums
    "CategoryEnum",
    "CustomerSegmentEnum",
    "DayOfWeekEnum",
    "OrderCategoryEnum",
    "OrderStatusEnum",
    "OrderTypeEnum",
    "PaymentMethodEnum",
    "PaymentStatusEnum",
    "RoleEnum",
    "TableStatusEnum",
    # models
    "Staff",
    "MenuItem",
    "Order",
    "OrderItem",
    "OrderFeedback",
    "Payment",
    "Customer",
    "Table",
    "InventoryItem",
    "Recipe",
    "RecipeIngredient",
    "WasteLog",
    "Settings",
]
