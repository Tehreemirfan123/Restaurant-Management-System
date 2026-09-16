"""Bootstrap script: create the initial admin account and sample menu.

Run once after the database is up:
    python -m backend.seed

Reads SEED_ADMIN_USERNAME / SEED_ADMIN_PASSWORD from the environment
(falling back to admin / admin123). It is safe to run repeatedly:
existing rows are left untouched.
"""

import os

from backend.database.database import Base, SessionLocal, engine
from backend.models.models import CategoryEnum, MenuItem, RoleEnum, Staff
from backend.schemas.schemas import StaffCreate
from backend.services.staff_service import (
    create_staff,
    get_staff_by_username,
)


SAMPLE_MENU = [
    ("Chicken Biryani", "Traditional spicy chicken biryani with raita", 350, CategoryEnum.mains),
    ("Beef Burger", "Juicy beef burger with fries", 500, CategoryEnum.mains),
    ("Spring Rolls", "Crispy vegetable spring rolls", 200, CategoryEnum.starters),
    ("Gulab Jamun", "Warm syrup-soaked dessert", 150, CategoryEnum.desserts),
    ("Fresh Lime Soda", "Chilled sweet-and-salty lime soda", 120, CategoryEnum.drinks),
]


def seed():
    Base.metadata.create_all(bind=engine)

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
            for name, desc, price, category in SAMPLE_MENU:
                db.add(
                    MenuItem(
                        name=name,
                        description=desc,
                        price=price,
                        category=category,
                        available=True,
                    )
                )
            db.commit()
            print(f"Added {len(SAMPLE_MENU)} sample menu items.")
        else:
            print("Menu already has items, skipping sample data.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
