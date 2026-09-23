import enum


class CategoryEnum(str, enum.Enum):
    starters = "starters"
    mains = "mains"
    desserts = "desserts"
    drinks = "drinks"


class OrderStatusEnum(str, enum.Enum):
    received = "received"
    preparing = "preparing"
    ready = "ready"
    delivered = "delivered"
    cancelled = "cancelled"


class PaymentMethodEnum(str, enum.Enum):
    cash = "cash"
    card = "card"
    bank_transfer = "bank_transfer"
    online = "online"
    jazzcash = "jazzcash"
    easypaisa = "easypaisa"


class PaymentStatusEnum(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class RoleEnum(str, enum.Enum):
    admin = "admin"
    staff = "staff"


class TableStatusEnum(str, enum.Enum):
    available = "available"
    occupied = "occupied"
    reserved = "reserved"


class OrderTypeEnum(str, enum.Enum):
    # pickup/delivery are the live fulfilment types for the home kitchen.
    # dine_in/takeaway are kept for backwards compatibility but hidden in the UI.
    pickup = "pickup"
    delivery = "delivery"
    dine_in = "dine_in"
    takeaway = "takeaway"


class OrderCategoryEnum(str, enum.Enum):
    # Regular orders may pay cash on delivery. Custom / subscription orders
    # (and any order over the large-order threshold) require an advance.
    regular = "regular"
    custom = "custom"
    subscription = "subscription"
    large = "large"


class DayOfWeekEnum(str, enum.Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class CustomerSegmentEnum(str, enum.Enum):
    office = "office"
    student = "student"
    hostel = "hostel"
    household = "household"
    other = "other"
