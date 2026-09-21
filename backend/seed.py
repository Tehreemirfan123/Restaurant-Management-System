"""Bootstrap script: create the initial admin account and sample menu.

Run once after the database is up (from the backend/ directory):
    python seed.py

Reads SEED_ADMIN_USERNAME / SEED_ADMIN_PASSWORD from the environment
(falling back to admin / admin123). It is safe to run repeatedly:
existing rows are left untouched.
"""

import os

from database.database import SessionLocal
from models.models import (
    CategoryEnum,
    DayOfWeekEnum,
    InventoryItem,
    MenuItem,
    RoleEnum,
    Staff,
    Table,
)
from schemas.schemas import StaffCreate
from services.staff_service import (
    create_staff,
    get_staff_by_username,
)


# The real rotating weekly menu
# (name, description, price, category, day, packaging_cost).
# A null day means it's available any day (advance-order special).
SAMPLE_MENU = [
    ("Channa Pilao", "Channa pilao with raita and salad", 300, CategoryEnum.mains, DayOfWeekEnum.friday, 30),
    ("Chicken Nihari", "Special slow-cooked chicken nihari", 260, CategoryEnum.mains, DayOfWeekEnum.saturday, 30),
    ("Chicken Biryani", "Traditional spicy chicken biryani", 320, CategoryEnum.mains, DayOfWeekEnum.sunday, 30),
    ("Ghoota Daal (Chicken)", "Ghoota daal with chicken, served with chawal", 270, CategoryEnum.mains, DayOfWeekEnum.monday, 30),
    ("Sabzi / Daal", "Sabzi, daal mash or daal channa fry", 160, CategoryEnum.mains, DayOfWeekEnum.tuesday, 25),
    ("Chicken White Karahi", "Creamy chicken white karahi", 230, CategoryEnum.mains, DayOfWeekEnum.wednesday, 30),
    ("Karri Pakora", "Karri pakora with 2 roti / masar chawal", 220, CategoryEnum.mains, DayOfWeekEnum.thursday, 25),
    ("Mutton Kunna", "Available on advance order. Ask for details.", 700, CategoryEnum.mains, None, 40),
]

# (number, capacity)
SAMPLE_TABLES = [(1, 2), (2, 4), (3, 4), (4, 6), (5, 8)]

# (name, unit, quantity, reorder_level, unit_cost)
SAMPLE_INVENTORY = [
    ("Rice", "kg", 50, 10, 200),
    ("Chicken", "kg", 30, 8, 600),
    ("Flour", "kg", 40, 10, 120),
    ("Cooking Oil", "litre", 25, 5, 550),
    ("Sugar", "kg", 20, 5, 150),
]


def seed():
    # The schema is owned by Alembic; run `alembic upgrade head` first.
    db = SessionLocal()

    try:
        username = os.getenv("SEED_ADMIN_USERNAME", "admin")
        password = os.getenv("SEED_ADMIN_PASSWORD", "admin123")

        if get_staff_by_username(db, username) is None:
            create_staff(
                db,
                StaffCreate(
                    username=username,
                    full_name="Restaurant Admin",
                    password=password,
                    role=RoleEnum.admin,
                ),
            )
            print(f"Created admin user: {username} / {password}")
        else:
            print(f"Admin user '{username}' already exists, skipping.")

        if db.query(MenuItem).count() == 0:
            for name, desc, price, category, day, packaging in SAMPLE_MENU:
                db.add(
                    MenuItem(
                        name=name,
                        description=desc,
                        price=price,
                        category=category,
                        day_of_week=day,
                        packaging_cost=packaging,
                        available=True,
                    )
                )
            db.commit()
            print(f"Added {len(SAMPLE_MENU)} sample menu items.")
        else:
            print("Menu already has items, skipping sample data.")

        if db.query(Table).count() == 0:
            for number, capacity in SAMPLE_TABLES:
                db.add(Table(number=number, capacity=capacity))
            db.commit()
            print(f"Added {len(SAMPLE_TABLES)} sample tables.")
        else:
            print("Tables already exist, skipping sample data.")

        if db.query(InventoryItem).count() == 0:
            for name, unit, qty, reorder, cost in SAMPLE_INVENTORY:
                db.add(
                    InventoryItem(
                        name=name,
                        unit=unit,
                        quantity=qty,
                        reorder_level=reorder,
                        unit_cost=cost,
                    )
                )
            db.commit()
            print(f"Added {len(SAMPLE_INVENTORY)} sample inventory items.")
        else:
            print("Inventory already has items, skipping sample data.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
