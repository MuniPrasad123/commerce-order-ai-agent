"""Tests for the agent card configuration, system prompt, and agent structure."""

import sys
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


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


class TestSystemPrompt:
    """Tests for the agent system prompt content."""

    def test_system_prompt_contains_commerce_order_assistant(self, add_app_to_path):
        from agent import get_system_prompt
        prompt = get_system_prompt()
        assert "CommerceOrderAssistant" in prompt

    def test_system_prompt_instructs_tool_use(self, add_app_to_path):
        from agent import get_system_prompt
        prompt = get_system_prompt()
        assert "get_order_status" in prompt or "MUST use" in prompt

    def test_system_prompt_covers_unknown_order_edge_case(self, add_app_to_path):
        from agent import get_system_prompt
        prompt = get_system_prompt()
        lower = prompt.lower()
        assert "not found" in lower or "wasn't able to find" in lower or "not find" in lower

    def test_system_prompt_covers_missing_order_id_edge_case(self, add_app_to_path):
        from agent import get_system_prompt
        prompt = get_system_prompt()
        lower = prompt.lower()
        assert "order id" in lower

    def test_system_prompt_defines_scope_boundary(self, add_app_to_path):
        from agent import get_system_prompt
        prompt = get_system_prompt()
        lower = prompt.lower()
        assert "cancellation" in lower or "return" in lower or "scope" in lower

    def test_system_prompt_forbids_data_fabrication(self, add_app_to_path):
        from agent import get_system_prompt
        prompt = get_system_prompt()
        assert "Never fabricate" in prompt or "never fabricate" in prompt.lower()

    def test_system_prompt_is_non_empty(self, add_app_to_path):
        from agent import get_system_prompt
        prompt = get_system_prompt()
        assert len(prompt) > 100


class TestAgentStructure:
    """Tests for agent module structure and tool registration."""

    def test_get_order_status_tool_imported_in_agent(self, add_app_to_path):
        """Agent module must import get_order_status."""
        import agent as agent_module
        assert hasattr(agent_module, "get_order_status")

    def test_sample_agent_class_exists(self, add_app_to_path):
        """SampleAgent class must be defined."""
        from agent import SampleAgent
        assert SampleAgent is not None

    def test_agent_response_dataclass_exists(self, add_app_to_path):
        """AgentResponse dataclass must be defined."""
        from agent import AgentResponse
        assert AgentResponse is not None

    def test_agent_response_has_status_field(self, add_app_to_path):
        from agent import AgentResponse
        resp = AgentResponse(status="completed", message="ok")
        assert resp.status == "completed"
        assert resp.message == "ok"

    def test_sample_agent_instantiates(self, add_app_to_path):
        """SampleAgent should instantiate without errors when LLM is mocked."""
        with patch("agent.ChatLiteLLM", MagicMock()), \
             patch("agent.create_checkpointer", MagicMock()), \
             patch("agent.SummarizationMiddleware", MagicMock()):
            from agent import SampleAgent
            agent = SampleAgent()
            assert agent is not None

    def test_sample_agent_has_stream_method(self, add_app_to_path):
        from agent import SampleAgent
        assert hasattr(SampleAgent, "stream")

    def test_sample_agent_has_invoke_method(self, add_app_to_path):
        from agent import SampleAgent
        assert hasattr(SampleAgent, "invoke")

    def test_sample_agent_has_run_agent_helper(self, add_app_to_path):
        """_run_agent must exist as a plain async method (not a generator)."""
        from agent import SampleAgent
        assert hasattr(SampleAgent, "_run_agent")

    def test_order_lookup_tool_importable(self, add_app_to_path):
        """order_lookup_tool module must be importable."""
        import order_lookup_tool
        assert hasattr(order_lookup_tool, "get_order_status")


class TestMainConfiguration:
    """Tests for the main.py A2A agent card configuration (via source inspection)."""

    def test_main_references_correct_agent_name(self):
        main_path = Path(__file__).parent.parent / "app" / "main.py"
        source = main_path.read_text()
        assert "commerce-order-assistant-agent" in source

    def test_main_references_version(self):
        main_path = Path(__file__).parent.parent / "app" / "main.py"
        source = main_path.read_text()
        assert "1.0.0" in source

    def test_main_references_order_tracking(self):
        main_path = Path(__file__).parent.parent / "app" / "main.py"
        source = main_path.read_text()
        assert "order" in source.lower()

    def test_main_calls_bootstrap(self):
        main_path = Path(__file__).parent.parent / "app" / "main.py"
        source = main_path.read_text()
        assert "bootstrap(app)" in source

    def test_well_known_agent_json_path_used_in_probes(self):
        """asset.yaml should use /.well-known/agent.json for probes."""
        asset_path = Path(__file__).parent.parent / "asset.yaml"
        if asset_path.exists():
            source = asset_path.read_text()
            assert "/.well-known/agent.json" in source
