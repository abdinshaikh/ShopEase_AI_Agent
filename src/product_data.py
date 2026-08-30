
PRODUCTS = {
    "Laptop": {
        "price": 65000,
        "category": "Electronics"
    },
    "Wireless Headphones": {
        "price": 2500,
        "category": "Electronics"
    },
    "Mechanical Keyboard": {
        "price": 4500,
        "category": "Electronics"
    },
    "Gaming Mouse": {
        "price": 1800,
        "category": "Electronics"
    }
}


def get_product_info(product_name: str) -> str:
    """Return product price and category."""

    product = PRODUCTS.get(product_name)

    if product is None:
        return f"Product '{product_name}' was not found."

    return (
        f"{product_name}: "
        f"₹{product['price']}, "
        f"Category: {product['category']}"
    )
