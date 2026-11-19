import unittest

from app.order_lookup import lookup_order


class OrderLookupTests(unittest.TestCase):
    def test_normalizes_case_and_whitespace(self):
        self.assertEqual(
            lookup_order(" ord-0003 "),
            {
                "found": True,
                "order_id": "ORD-0003",
                "status": "Shipped",
                "estimated_delivery_date": "2026-11-22",
                "item_description": "Portable Laptop Stand",
            },
        )

    def test_cancelled_order_has_no_delivery_estimate(self):
        order = lookup_order("ORD-0006")
        self.assertEqual(order["status"], "Cancelled")
        self.assertEqual(order["estimated_delivery_date"], "N/A")

    def test_missing_order_returns_only_lookup_metadata(self):
        for order_id in ("ORD-9999", "", "   "):
            with self.subTest(order_id=order_id):
                self.assertEqual(
                    lookup_order(order_id), {"found": False, "order_id": order_id}
                )

    def test_changing_a_result_does_not_change_the_dataset(self):
        order = lookup_order("ORD-0003")
        order["status"] = "Changed"
        self.assertEqual(lookup_order("ORD-0003")["status"], "Shipped")
