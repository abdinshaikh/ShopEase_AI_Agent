
from src.tools import (
    check_order_status,
    get_order_details,
    check_cancellation_eligibility,
    cancel_order
)

from config.settings import DB_PATH


def check_order_status_tool(order_id: str) -> str:
    """Check the current status of a ShopEase order using its order ID."""
    return check_order_status(order_id, DB_PATH)


def get_order_details_tool(order_id: str) -> str:
    """Get the product, quantity, price, and status of a ShopEase order."""
    return get_order_details(order_id, DB_PATH)


def check_cancellation_eligibility_tool(order_id: str) -> str:
    """Check whether a ShopEase order can currently be cancelled."""
    return check_cancellation_eligibility(order_id, DB_PATH)


def cancel_order_tool(order_id: str) -> str:
    """Cancel a ShopEase order if it is eligible for cancellation."""
    return cancel_order(order_id, DB_PATH)



from src.product_data import get_product_info


def get_product_info_tool(product_name: str) -> str:
    """Get the price and category of a ShopEase product."""
    return get_product_info(product_name)


from src.policy_data import get_return_policy


def get_return_policy_tool() -> str:
    """Get the current ShopEase return policy."""
    return get_return_policy()
