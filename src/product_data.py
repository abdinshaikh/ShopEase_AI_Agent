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


PRODUCT_ALIASES = {
    "laptop": "Laptop",

    "headphones": "Wireless Headphones",
    "wireless headphone": "Wireless Headphones",
    "wireless headphones": "Wireless Headphones",

    "keyboard": "Mechanical Keyboard",
    "mechanical keyboard": "Mechanical Keyboard",

    "mouse": "Gaming Mouse",
    "gaming mouse": "Gaming Mouse"
}


def get_product_info(product_name: str) -> str:
    """Return product price and category."""

    if not product_name:
        return "Product name was not provided."

    normalized_name = (
        product_name
        .strip()
        .casefold()
    )

    # First try known aliases.
    matched_product_name = PRODUCT_ALIASES.get(
        normalized_name
    )

    # If it is not an alias, check the actual
    # product names case-insensitively.
    if matched_product_name is None:

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
