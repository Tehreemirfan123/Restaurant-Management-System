"""Wipe transactional/test data to reach a clean production-ready state.

This removes the data that piles up while testing — orders, order items,
payments, feedback, waste logs and customers — but keeps the schema and all
configuration/catalog data intact: staff accounts, the menu, tables,
inventory, recipes and settings.

Run from the backend/ directory:
    python clean_data.py            # asks for confirmation
    python clean_data.py --yes      # skip the prompt (for scripts)
"""

import sys

from database.database import SessionLocal
from models.models import (
    Customer,
    Order,
    OrderFeedback,
    OrderItem,
    Payment,
    WasteLog,
)


# Deleted in FK-safe order (children before parents).
WIPE = [
    ("payments", Payment),
    ("order feedback", OrderFeedback),
    ("order items", OrderItem),
    ("waste logs", WasteLog),
    ("orders", Order),
    ("customers", Customer),
]


def clean(confirm: bool = True) -> None:
    db = SessionLocal()
    try:
        counts = {label: db.query(model).count() for label, model in WIPE}
        total = sum(counts.values())

        print("About to delete transactional/test data:")
        for label, _ in WIPE:
            print(f"  - {counts[label]:>5}  {label}")
        print("Keeping: staff, menu, tables, inventory, recipes, settings.")

        if total == 0:
            print("Nothing to delete — database is already clean.")
            return

        if confirm:
            answer = input("Type 'clean' to proceed: ").strip().lower()
            if answer != "clean":
                print("Aborted.")
                return

        for label, model in WIPE:
            deleted = db.query(model).delete(synchronize_session=False)
            print(f"Deleted {deleted} {label}.")

        db.commit()
        print("Done. Database is now in a clean production-ready state.")
    finally:
        db.close()


if __name__ == "__main__":
    clean(confirm="--yes" not in sys.argv)
