
import sqlite3


def get_connection(db_path):
    return sqlite3.connect(db_path)


def get_order(order_id, db_path):
    connection = get_connection(db_path)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT order_id, customer_id, product, quantity, price, status
        FROM orders
        WHERE order_id = ?
        """,
        (order_id,)
    )

    result = cursor.fetchone()

    connection.close()

    return result
