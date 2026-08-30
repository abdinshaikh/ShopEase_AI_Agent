
import sqlite3

from src.database import get_order


def check_order_status(order_id, db_path):
    """Check the current status of an order."""

    order = get_order(order_id, db_path)

    if order is None:
        return "Order not found."

    return order[5]


def get_order_details(order_id, db_path):
    """Get complete information about an order."""

    order = get_order(order_id, db_path)

    if order is None:
        return "Order not found."

    order_id, customer_id, product, quantity, price, status = order

    return (
        f"Order ID: {order_id}\n"
        f"Product: {product}\n"
        f"Quantity: {quantity}\n"
        f"Price: ₹{price}\n"
        f"Status: {status}"
    )


def check_cancellation_eligibility(order_id, db_path):
    """Check whether an order can currently be cancelled."""

    order = get_order(order_id, db_path)

    if order is None:
        return "Order not found."

    status = order[5]

    if status == "Processing":
        return "Order can be cancelled."

    if status == "Shipped":
        return "Order cannot be cancelled because it has already shipped."

    if status == "Delivered":
        return "Order cannot be cancelled because it has already been delivered."

    if status == "Cancelled":
        return "Order is already cancelled."

    return f"Order cannot be cancelled because its status is {status}."


def cancel_order(order_id, db_path):
    """Cancel an order if it is still processing."""

    order = get_order(order_id, db_path)

    if order is None:
        return "Order not found."

    status = order[5]

    if status == "Cancelled":
        return "Order is already cancelled."

    if status != "Processing":
        return f"Order cannot be cancelled because it is already {status.lower()}."

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE orders SET status = ? WHERE order_id = ?",
        ("Cancelled", order_id)
    )

    connection.commit()
    connection.close()

    return f"Order {order_id} has been cancelled successfully."
