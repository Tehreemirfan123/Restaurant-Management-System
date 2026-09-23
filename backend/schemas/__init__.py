"""Schema package.

Pydantic schemas are split into domain modules and re-exported here so that
both ``from schemas import X`` and ``from schemas.schemas import X`` keep
working unchanged.
"""

from schemas.menu import MenuItemCreate, MenuItemResponse, MenuItemUpdate
from schemas.order import (
    OrderCreate,
    OrderItemCreate,
    OrderItemResponse,
    OrderResponse,
    OrderStatusUpdate,
)
from schemas.payment import (
    CheckoutRequest,
    CheckoutResponse,
    CheckoutStatus,
    MethodTotal,
    OutstandingOrder,
    PaymentCreate,
    PaymentReconciliation,
    PaymentResponse,
    PaymentUpdate,
)
from schemas.staff import LoginRequest, StaffCreate, StaffResponse, Token
from schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from schemas.table import TableCreate, TableResponse, TableUpdate
from schemas.inventory import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
)
from schemas.waste import WasteLogCreate, WasteLogResponse
from schemas.recipe import (
    RecipeCreate,
    RecipeIngredientCreate,
    RecipeIngredientResponse,
    RecipeResponse,
    RecipeUpdate,
)
from schemas.reports import DishCosting, LowStockItem, ReportsSummary, TopItem
from schemas.feedback import FeedbackCreate, FeedbackResponse
from schemas.settings import OrderingStatus, SettingsResponse, SettingsUpdate

__all__ = [
    "MenuItemCreate",
    "MenuItemUpdate",
    "MenuItemResponse",
    "OrderItemCreate",
    "OrderCreate",
    "OrderItemResponse",
    "OrderResponse",
    "OrderStatusUpdate",
    "PaymentCreate",
    "PaymentUpdate",
    "CheckoutRequest",
    "CheckoutResponse",
    "CheckoutStatus",
    "PaymentResponse",
    "MethodTotal",
    "OutstandingOrder",
    "PaymentReconciliation",
    "StaffCreate",
    "StaffResponse",
    "LoginRequest",
    "Token",
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "TableCreate",
    "TableUpdate",
    "TableResponse",
    "InventoryItemCreate",
    "InventoryItemUpdate",
    "InventoryItemResponse",
    "WasteLogCreate",
    "WasteLogResponse",
    "RecipeIngredientCreate",
    "RecipeCreate",
    "RecipeUpdate",
    "RecipeIngredientResponse",
    "RecipeResponse",
    "TopItem",
    "LowStockItem",
    "ReportsSummary",
    "DishCosting",
    "FeedbackCreate",
    "FeedbackResponse",
    "SettingsUpdate",
    "SettingsResponse",
    "OrderingStatus",
]
