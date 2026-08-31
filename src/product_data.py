
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

    if not product_name:
        return "Product name was not provided."

    # Normalize the user's/tool's product name.
    normalized_name = (
        product_name
        .strip()
        .casefold()
    )

    # Find the canonical product name
    # using a case-insensitive comparison.
    matched_product_name = None

    for name in PRODUCTS:

        if name.casefold() == normalized_name:

            matched_product_name = name
            break

    if matched_product_name is None:

        return (
            f"Product '{product_name}' "
            "was not found."
        )

    product = PRODUCTS[
        matched_product_name
    ]

    return (
        f"{matched_product_name}: "
        f"₹{product['price']}, "
        f"Category: {product['category']}"
    )
