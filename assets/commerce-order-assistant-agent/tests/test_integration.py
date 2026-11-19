"""Integration tests for the CommerceOrderAssistant agent.

These tests exercise the end-to-end agent flow with a mocked LLM.
All external systems (AI Core, MCP Gateway) are mocked — tests run offline.
"""

import sys
import pytest
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture(autouse=True)
def add_app_to_path():
    """Add app/ to sys.path so peer-level imports work (mirrors runtime behaviour)."""
    app_path = str(Path(__file__).parent.parent / "app")
    added = False
    if app_path not in sys.path:
        sys.path.insert(0, app_path)
        added = True
    yield
    if added and app_path in sys.path:
        sys.path.remove(app_path)


def _make_llm_response(content: str):
    """Create a minimal mock LLM final message."""
    msg = MagicMock()
    msg.content = content
    return msg


def _make_tool_call_message(tool_name: str, args: dict):
    """Create a mock AI message with a tool call."""
    tool_call = MagicMock()
    tool_call.name = tool_name
    tool_call.args = args
    tool_call.id = "tc-001"

    msg = MagicMock()
    msg.content = ""
    msg.tool_calls = [tool_call]
    return msg


def _make_tool_result_message(tool_name: str, result: dict):
    """Create a mock tool result message."""
    msg = MagicMock()
    msg.content = str(result)
    msg.name = tool_name
    msg.tool_calls = []
    return msg


class TestScenario1HappyPath:
    """Scenario 1: Customer asks about a specific order with order ID provided."""

    @pytest.mark.asyncio
    async def test_known_order_id_returns_status_and_delivery(self, add_app_to_path):
        """When customer provides ORD-0001, agent returns status and delivery date."""
        from agent import SampleAgent, AgentResponse

        # Build mock message chain: tool call → tool result → final response
        tool_call_msg = _make_tool_call_message("get_order_status", {"order_id": "ORD-0001"})
        tool_result_msg = _make_tool_result_message(
            "get_order_status",
            {"found": True, "order_id": "ORD-0001", "status": "Delivered",
             "estimated_delivery_date": "2026-11-10", "item_description": "Wireless Bluetooth Headphones"}
        )
        final_msg = _make_llm_response(
            "Your order ORD-0001 (Wireless Bluetooth Headphones) has been Delivered. "
            "It was estimated to arrive by November 10, 2026."
        )

        mock_graph_result = {
            "messages": [tool_call_msg, tool_result_msg, final_msg]
        }

        with patch("agent.ChatLiteLLM", MagicMock()), \
             patch("agent.create_checkpointer", MagicMock()), \
             patch("agent.SummarizationMiddleware", MagicMock()), \
             patch("agent.create_agent") as mock_create_agent, \
             patch("agent.get_user_sub", return_value="test-user"):

            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value=mock_graph_result)
            mock_create_agent.return_value = mock_graph

            agent = SampleAgent()
            response = await agent.invoke(
                query="Where is my order ORD-0001?",
                context_id="test-ctx-1",
            )

        assert response.status == "completed"
        assert "ORD-0001" in response.message or "Delivered" in response.message

    @pytest.mark.asyncio
    async def test_shipped_order_returns_delivery_estimate(self, add_app_to_path):
        """When customer asks about ORD-0003 (Shipped), agent returns expected delivery date."""
        from agent import SampleAgent

        tool_call_msg = _make_tool_call_message("get_order_status", {"order_id": "ORD-0003"})
        tool_result_msg = _make_tool_result_message(
            "get_order_status",
            {"found": True, "order_id": "ORD-0003", "status": "Shipped",
             "estimated_delivery_date": "2026-11-22", "item_description": "Portable Laptop Stand"}
        )
        final_msg = _make_llm_response(
            "Your order ORD-0003 (Portable Laptop Stand) is currently Shipped. "
            "Estimated delivery: November 22, 2026."
        )

        mock_graph_result = {
            "messages": [tool_call_msg, tool_result_msg, final_msg]
        }

        with patch("agent.ChatLiteLLM", MagicMock()), \
             patch("agent.create_checkpointer", MagicMock()), \
             patch("agent.SummarizationMiddleware", MagicMock()), \
             patch("agent.create_agent") as mock_create_agent, \
             patch("agent.get_user_sub", return_value="test-user"):

            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value=mock_graph_result)
            mock_create_agent.return_value = mock_graph

            agent = SampleAgent()
            response = await agent.invoke(
                query="When will ORD-0003 arrive?",
                context_id="test-ctx-2",
            )

        assert response.status == "completed"
        assert "Shipped" in response.message or "2026" in response.message


class TestScenario2MissingOrderId:
    """Scenario 2: Customer asks without order ID, then provides it."""

    @pytest.mark.asyncio
    async def test_agent_prompts_for_order_id_when_not_provided(self, add_app_to_path):
        """When customer says 'track my order' without an ID, agent asks for it."""
        from agent import SampleAgent

        # First turn: no tool call — agent asks for order ID
        prompt_msg = _make_llm_response(
            "I'd be happy to help you track your order! Could you please provide your order ID? "
            "You can find it in your confirmation email, usually formatted as ORD-XXXX."
        )
        prompt_msg.tool_calls = []

        mock_graph_result = {"messages": [prompt_msg]}

        with patch("agent.ChatLiteLLM", MagicMock()), \
             patch("agent.create_checkpointer", MagicMock()), \
             patch("agent.SummarizationMiddleware", MagicMock()), \
             patch("agent.create_agent") as mock_create_agent, \
             patch("agent.get_user_sub", return_value="test-user"):

            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value=mock_graph_result)
            mock_create_agent.return_value = mock_graph

            agent = SampleAgent()
            response = await agent.invoke(
                query="Track my order",
                context_id="test-ctx-3",
            )

        assert response.status == "completed"
        lower = response.message.lower()
        assert "order id" in lower or "ord-" in lower or "order" in lower

    @pytest.mark.asyncio
    async def test_agent_returns_result_after_customer_provides_id(self, add_app_to_path):
        """After the customer provides ORD-0005, agent returns order details."""
        from agent import SampleAgent

        tool_call_msg = _make_tool_call_message("get_order_status", {"order_id": "ORD-0005"})
        tool_result_msg = _make_tool_result_message(
            "get_order_status",
            {"found": True, "order_id": "ORD-0005", "status": "Shipped",
             "estimated_delivery_date": "2026-11-21", "item_description": "Ergonomic Office Chair"}
        )
        final_msg = _make_llm_response(
            "Your order ORD-0005 (Ergonomic Office Chair) is currently Shipped "
            "and estimated to arrive by November 21, 2026."
        )

        mock_graph_result = {
            "messages": [tool_call_msg, tool_result_msg, final_msg]
        }

        with patch("agent.ChatLiteLLM", MagicMock()), \
             patch("agent.create_checkpointer", MagicMock()), \
             patch("agent.SummarizationMiddleware", MagicMock()), \
             patch("agent.create_agent") as mock_create_agent, \
             patch("agent.get_user_sub", return_value="test-user"):

            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value=mock_graph_result)
            mock_create_agent.return_value = mock_graph

            agent = SampleAgent()
            response = await agent.invoke(
                query="My order ID is ORD-0005",
                context_id="test-ctx-3",
            )

        assert response.status == "completed"
        assert "ORD-0005" in response.message or "Shipped" in response.message


class TestScenario3UnknownOrderId:
    """Scenario 3: Customer provides an order ID that does not exist in mock data."""

    @pytest.mark.asyncio
    async def test_unknown_order_id_returns_not_found_message(self, add_app_to_path):
        """When customer provides ORD-9999 (unknown), agent returns a not-found message."""
        from agent import SampleAgent

        tool_call_msg = _make_tool_call_message("get_order_status", {"order_id": "ORD-9999"})
        tool_result_msg = _make_tool_result_message(
            "get_order_status",
            {"found": False, "order_id": "ORD-9999"}
        )
        final_msg = _make_llm_response(
            "I wasn't able to find an order with the ID ORD-9999. "
            "Please double-check your order ID and try again, "
            "or contact our support team for further assistance."
        )
        final_msg.tool_calls = []

        mock_graph_result = {
            "messages": [tool_call_msg, tool_result_msg, final_msg]
        }

        with patch("agent.ChatLiteLLM", MagicMock()), \
             patch("agent.create_checkpointer", MagicMock()), \
             patch("agent.SummarizationMiddleware", MagicMock()), \
             patch("agent.create_agent") as mock_create_agent, \
             patch("agent.get_user_sub", return_value="test-user"):

            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value=mock_graph_result)
            mock_create_agent.return_value = mock_graph

            agent = SampleAgent()
            response = await agent.invoke(
                query="Check status for ORD-9999",
                context_id="test-ctx-4",
            )

        assert response.status == "completed"
        lower = response.message.lower()
        assert "not find" in lower or "wasn't able" in lower or "not found" in lower or "9999" in lower

    @pytest.mark.asyncio
    async def test_unknown_order_message_does_not_contain_fabricated_data(self, add_app_to_path):
        """The not-found response must not contain invented order status or delivery dates."""
        from agent import SampleAgent

        tool_call_msg = _make_tool_call_message("get_order_status", {"order_id": "ORD-9999"})
        tool_result_msg = _make_tool_result_message(
            "get_order_status",
            {"found": False, "order_id": "ORD-9999"}
        )
        final_msg = _make_llm_response(
            "I wasn't able to find an order with ID ORD-9999. "
            "Please verify your order ID or contact support."
        )
        final_msg.tool_calls = []

        mock_graph_result = {
            "messages": [tool_call_msg, tool_result_msg, final_msg]
        }

        with patch("agent.ChatLiteLLM", MagicMock()), \
             patch("agent.create_checkpointer", MagicMock()), \
             patch("agent.SummarizationMiddleware", MagicMock()), \
             patch("agent.create_agent") as mock_create_agent, \
             patch("agent.get_user_sub", return_value="test-user"):

            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value=mock_graph_result)
            mock_create_agent.return_value = mock_graph

            agent = SampleAgent()
            response = await agent.invoke(
                query="Check status for ORD-9999",
                context_id="test-ctx-5",
            )

        assert response.status == "completed"
        # Response should not contain fake status values
        assert "Processing" not in response.message
        assert "Delivered" not in response.message
        assert "Shipped" not in response.message


class TestAgentStreamBehaviour:
    """Tests for the stream() method yielding protocol-compliant responses."""

    @pytest.mark.asyncio
    async def test_stream_yields_processing_then_completed(self, add_app_to_path):
        """stream() must yield a 'Processing...' chunk first, then a completed response."""
        from agent import SampleAgent

        final_msg = _make_llm_response("Your order ORD-0002 is Out for Delivery.")
        final_msg.tool_calls = []
        mock_graph_result = {"messages": [final_msg]}

        with patch("agent.ChatLiteLLM", MagicMock()), \
             patch("agent.create_checkpointer", MagicMock()), \
             patch("agent.SummarizationMiddleware", MagicMock()), \
             patch("agent.create_agent") as mock_create_agent, \
             patch("agent.get_user_sub", return_value="test-user"):

            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value=mock_graph_result)
            mock_create_agent.return_value = mock_graph

            agent = SampleAgent()
            chunks = []
            async for chunk in agent.stream("Status of ORD-0002?", "ctx-stream"):
                chunks.append(chunk)

        assert len(chunks) >= 2
        assert chunks[0]["is_task_complete"] is False
        assert "Processing" in chunks[0]["content"]
        assert chunks[-1]["is_task_complete"] is True

    @pytest.mark.asyncio
    async def test_stream_handles_exception_gracefully(self, add_app_to_path):
        """stream() must yield a graceful error response on unexpected exceptions."""
        from agent import SampleAgent

        with patch("agent.ChatLiteLLM", MagicMock()), \
             patch("agent.create_checkpointer", MagicMock()), \
             patch("agent.SummarizationMiddleware", MagicMock()), \
             patch("agent.create_agent") as mock_create_agent, \
             patch("agent.get_user_sub", return_value="test-user"):

            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(side_effect=RuntimeError("Unexpected failure"))
            mock_create_agent.return_value = mock_graph

            agent = SampleAgent()
            chunks = []
            async for chunk in agent.stream("Status of ORD-0001?", "ctx-err"):
                chunks.append(chunk)

        completed_chunks = [c for c in chunks if c["is_task_complete"]]
        assert len(completed_chunks) == 1
        assert "error" in completed_chunks[0]["content"].lower() or "encountered" in completed_chunks[0]["content"].lower()
