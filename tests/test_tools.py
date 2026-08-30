
import sqlite3

from src.tools import (
    check_order_status,
    get_order_details,
    check_cancellation_eligibility,
    cancel_order,
)


def create_test_database(db_path):

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            product TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)

    test_orders = [
        ("TEST_SHIPPED", "C001", "Laptop", 1, 65000.0, "Shipped"),
        ("TEST_PROCESSING", "C001", "Mouse", 2, 1800.0, "Processing"),
        ("TEST_CANCELLED", "C001", "Keyboard", 1, 4500.0, "Cancelled"),
        ("TEST_DELIVERED", "C001", "Headphones", 1, 2500.0, "Delivered"),
    ]

    cursor.executemany(
        """
        INSERT INTO orders
        (order_id, customer_id, product, quantity, price, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        test_orders
    )

    connection.commit()
    connection.close()


def test_check_order_status(tmp_path):

    db_path = str(tmp_path / "test.db")

    create_test_database(db_path)

    result = check_order_status(
        "TEST_SHIPPED",
        db_path
    )

    assert result == "Shipped"


def test_get_order_details(tmp_path):

    db_path = str(tmp_path / "test.db")

    create_test_database(db_path)

    result = get_order_details(
        "TEST_SHIPPED",
        db_path
    )

    assert "Order ID: TEST_SHIPPED" in result
    assert "Product: Laptop" in result
    assert "Quantity: 1" in result
    assert "Price: ₹65000.0" in result
    assert "Status: Shipped" in result


def test_processing_order_can_be_cancelled(tmp_path):

    db_path = str(tmp_path / "test.db")

    create_test_database(db_path)

    result = check_cancellation_eligibility(
        "TEST_PROCESSING",
        db_path
    )

    assert result == "Order can be cancelled."


def test_shipped_order_cannot_be_cancelled(tmp_path):

    db_path = str(tmp_path / "test.db")

    create_test_database(db_path)

    result = check_cancellation_eligibility(
        "TEST_SHIPPED",
        db_path
    )

    assert result == (
        "Order cannot be cancelled because it has already shipped."
    )


def test_delivered_order_cannot_be_cancelled(tmp_path):

    db_path = str(tmp_path / "test.db")

    create_test_database(db_path)

    result = check_cancellation_eligibility(
        "TEST_DELIVERED",
        db_path
    )

    assert result == (
        "Order cannot be cancelled because it has already been delivered."
    )


def test_cancel_processing_order(tmp_path):

    db_path = str(tmp_path / "test.db")

    create_test_database(db_path)

    result = cancel_order(
        "TEST_PROCESSING",
        db_path
    )

    assert result == (
        "Order TEST_PROCESSING has been cancelled successfully."
    )

    status = check_order_status(
        "TEST_PROCESSING",
        db_path
    )

    assert status == "Cancelled"


def test_already_cancelled_order(tmp_path):

    db_path = str(tmp_path / "test.db")

    create_test_database(db_path)

    result = cancel_order(
        "TEST_CANCELLED",
        db_path
    )

    assert result == "Order is already cancelled."


def test_unknown_order(tmp_path):

    db_path = str(tmp_path / "test.db")

    create_test_database(db_path)

    status = check_order_status(
        "DOES_NOT_EXIST",
        db_path
    )

    details = get_order_details(
        "DOES_NOT_EXIST",
        db_path
    )

    eligibility = check_cancellation_eligibility(
        "DOES_NOT_EXIST",
        db_path
    )

    cancellation = cancel_order(
        "DOES_NOT_EXIST",
        db_path
    )

    assert status == "Order not found."
    assert details == "Order not found."
    assert eligibility == "Order not found."
    assert cancellation == "Order not found."
