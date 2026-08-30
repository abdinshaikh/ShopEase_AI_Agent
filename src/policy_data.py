
RETURN_POLICY = """
ShopEase accepts returns within 30 days of delivery for eligible products.
Items must generally be unused and in their original packaging.
"""


def get_return_policy() -> str:
    """Return the current ShopEase return policy."""
    return RETURN_POLICY.strip()
