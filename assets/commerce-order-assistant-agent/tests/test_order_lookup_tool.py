"""Unit tests for the get_order_status mock order lookup tool."""

import pytest
from app.order_lookup_tool import get_order_status


class TestGetOrderStatusFound:
    """Tests for successful order lookup scenarios."""

    def test_returns_found_true_for_known_order(self):
        result = get_order_status.invoke({"order_id": "ORD-0001"})
        assert result["found"] is True

    def test_returns_correct_order_id(self):
        result = get_order_status.invoke({"order_id": "ORD-0003"})
        assert result["order_id"] == "ORD-0003"

    def test_returns_status_field(self):
        result = get_order_status.invoke({"order_id": "ORD-0003"})
        assert "status" in result
        assert result["status"] == "Shipped"

    def test_returns_estimated_delivery_date_field(self):
        result = get_order_status.invoke({"order_id": "ORD-0003"})
        assert "estimated_delivery_date" in result
        assert result["estimated_delivery_date"] == "2026-11-22"

    def test_returns_item_description_field(self):
        result = get_order_status.invoke({"order_id": "ORD-0001"})
        assert "item_description" in result
        assert isinstance(result["item_description"], str)
        assert len(result["item_description"]) > 0

    def test_returns_all_required_fields_for_found_order(self):
        result = get_order_status.invoke({"order_id": "ORD-0005"})
        required_fields = {"order_id", "status", "estimated_delivery_date", "item_description", "found"}
        assert required_fields.issubset(result.keys())

    def test_delivered_order_status(self):
        result = get_order_status.invoke({"order_id": "ORD-0001"})
        assert result["status"] == "Delivered"

    def test_cancelled_order_status(self):
        result = get_order_status.invoke({"order_id": "ORD-0006"})
        assert result["status"] == "Cancelled"
        assert result["estimated_delivery_date"] == "N/A"

    def test_processing_order_status(self):
        result = get_order_status.invoke({"order_id": "ORD-0004"})
        assert result["status"] == "Processing"

    def test_out_for_delivery_status(self):
        result = get_order_status.invoke({"order_id": "ORD-0002"})
        assert result["status"] == "Out for Delivery"


class TestGetOrderStatusNotFound:
    """Tests for order not found scenarios."""

    def test_returns_found_false_for_unknown_order(self):
        result = get_order_status.invoke({"order_id": "ORD-9999"})
        assert result["found"] is False

    def test_returns_original_order_id_when_not_found(self):
        result = get_order_status.invoke({"order_id": "ORD-9999"})
        assert result["order_id"] == "ORD-9999"

    def test_not_found_has_no_status_field(self):
        result = get_order_status.invoke({"order_id": "ORD-XXXX"})
        assert "status" not in result

    def test_completely_invalid_id_not_found(self):
        result = get_order_status.invoke({"order_id": "INVALID-ID"})
        assert result["found"] is False


class TestGetOrderStatusCaseInsensitive:
    """Tests for case-insensitive order ID matching."""

    def test_lowercase_order_id_matches(self):
        result = get_order_status.invoke({"order_id": "ord-0001"})
        assert result["found"] is True
        assert result["order_id"] == "ORD-0001"

    def test_mixed_case_order_id_matches(self):
        result = get_order_status.invoke({"order_id": "Ord-0003"})
        assert result["found"] is True

    def test_uppercase_order_id_matches(self):
        result = get_order_status.invoke({"order_id": "ORD-0005"})
        assert result["found"] is True

    def test_lowercase_unknown_order_id_not_found(self):
        result = get_order_status.invoke({"order_id": "ord-9999"})
        assert result["found"] is False

    def test_whitespace_stripped_from_order_id(self):
        result = get_order_status.invoke({"order_id": "  ORD-0002  "})
        assert result["found"] is True
