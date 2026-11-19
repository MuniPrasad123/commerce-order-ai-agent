"""LangChain tool for looking up simulated order status."""

from langchain_core.tools import tool

if __package__:
    from .order_lookup import lookup_order
else:
    from order_lookup import lookup_order


@tool
def get_order_status(order_id: str) -> dict:
    """Look up the status and estimated delivery date for a given order ID.

    Args:
        order_id: The order identifier to look up (e.g., 'ORD-0001').
    """
    return lookup_order(order_id)
