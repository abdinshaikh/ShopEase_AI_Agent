import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

DATABASE_DIR = (
    PROJECT_ROOT / "database"
)

DB_PATH = (
    DATABASE_DIR / "shopease.db"
)


def initialize_database():

    DATABASE_DIR.mkdir(
        exist_ok=True
    )

    connection = sqlite3.connect(
        DB_PATH
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)

    existing_orders = cursor.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    if existing_orders == 0:

        orders = [
            (
                "12345",
                "C001",
                "Laptop",
                1,
                65000.0,
                "Shipped"
            ),
            (
                "12346",
                "C002",
                "Wireless Headphones",
                2,
                2500.0,
                "Delivered"
            ),
            (
                "12347",
                "C001",
                "Mechanical Keyboard",
                1,
                4500.0,
                "Cancelled"
            ),
            (
                "12348",
                "C003",
                "Gaming Mouse",
                1,
                1800.0,
                "Cancelled"
            )
        ]

        cursor.executemany(
            """
            INSERT INTO orders
            (
                order_id,
                customer_id,
                product,
                quantity,
                price,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            orders
        )

    connection.commit()
    connection.close()


if __name__ == "__main__":

    initialize_database()

    print(
        f"Database initialized: {DB_PATH}"
    )
