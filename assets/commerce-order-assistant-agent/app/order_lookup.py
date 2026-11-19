"""Read-only lookup against the simulated order dataset."""

import logging

logger = logging.getLogger(__name__)

# In-memory mock order dataset — 12 simulated orders
_ORDERS: dict[str, dict] = {
    "ORD-0001": {
        "order_id": "ORD-0001",
        "status": "Delivered",
        "estimated_delivery_date": "2026-11-10",
        "item_description": "Wireless Bluetooth Headphones",
    },
    "ORD-0002": {
        "order_id": "ORD-0002",
        "status": "Out for Delivery",
        "estimated_delivery_date": "2026-11-19",
        "item_description": "Running Shoes (Size 10)",
    },
    "ORD-0003": {
        "order_id": "ORD-0003",
        "status": "Shipped",
        "estimated_delivery_date": "2026-11-22",
        "item_description": "Portable Laptop Stand",
    },
    "ORD-0004": {
        "order_id": "ORD-0004",
        "status": "Processing",
        "estimated_delivery_date": "2026-11-25",
        "item_description": "Mechanical Keyboard",
    },
    "ORD-0005": {
        "order_id": "ORD-0005",
        "status": "Shipped",
        "estimated_delivery_date": "2026-11-21",
        "item_description": "Ergonomic Office Chair",
    },
    "ORD-0006": {
        "order_id": "ORD-0006",
        "status": "Cancelled",
        "estimated_delivery_date": "N/A",
        "item_description": "Smart Watch",
    },
    "ORD-0007": {
        "order_id": "ORD-0007",
        "status": "Processing",
        "estimated_delivery_date": "2026-11-27",
        "item_description": "USB-C Docking Station",
    },
    "ORD-0008": {
        "order_id": "ORD-0008",
        "status": "Out for Delivery",
        "estimated_delivery_date": "2026-11-19",
        "item_description": "Yoga Mat (Non-Slip)",
    },
    "ORD-0009": {
        "order_id": "ORD-0009",
        "status": "Delivered",
        "estimated_delivery_date": "2026-11-15",
        "item_description": "Coffee Maker (12-Cup)",
    },
    "ORD-0010": {
        "order_id": "ORD-0010",
        "status": "Shipped",
        "estimated_delivery_date": "2026-11-23",
        "item_description": "Noise-Cancelling Earbuds",
    },
    "ORD-0011": {
        "order_id": "ORD-0011",
        "status": "Processing",
        "estimated_delivery_date": "2026-11-28",
        "item_description": "4K Monitor (27-inch)",
    },
    "ORD-0012": {
        "order_id": "ORD-0012",
        "status": "Cancelled",
        "estimated_delivery_date": "N/A",
        "item_description": "Gaming Mouse",
    },
}


def lookup_order(order_id: str) -> dict:
    """Return a fresh result for a case-insensitive order ID."""
    normalized = order_id.strip().upper()
    logger.debug("Mock order lookup requested")

    order = _ORDERS.get(normalized)
    if order:
        logger.info("Order found: %s — status: %s", normalized, order["status"])
        return {**order, "found": True}

    logger.info("Mock order not found")
    return {"found": False, "order_id": order_id}
