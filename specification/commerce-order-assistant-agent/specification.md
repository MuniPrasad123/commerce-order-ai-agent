# Specification: commerce-order-assistant-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Basic Setup

- [x] Read `product-requirements-document.md` and `intent.md` to understand the full scope of the agent.
- [x] Bootstrap agent code in `assets/commerce-order-assistant-agent/` using instructions from the sap-agent-bootstrap section. (invoke from inside `assets/commerce-order-assistant-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

> **Decision**: The CommerceOrderAssistant has straightforward, single-step logic (ask for order ID → look up → respond). No complex multi-step workflows or domain-specific knowledge bases are required. Runtime skills are **not needed** for this agent.

---

## Project-Specific Tasks

### Mock Order Lookup Tool

- [x] Create `assets/commerce-order-assistant-agent/app/order_lookup_tool.py` implementing a Python function `get_order_status(order_id: str) -> dict` that:
  - Maintains an in-memory dataset of at least 10 simulated orders, each with the following fields:
    - `order_id` (string, e.g. `"ORD-0001"`)
    - `status` (one of: `"Processing"`, `"Shipped"`, `"Out for Delivery"`, `"Delivered"`, `"Cancelled"`)
    - `estimated_delivery_date` (string, e.g. `"2026-11-25"`)
    - `item_description` (string, brief description of the ordered item)
  - Returns the matching order record as a dict when the `order_id` is found.
  - Returns `{"found": false, "order_id": order_id}` when the `order_id` does not exist in the dataset.
  - Is case-insensitive when matching order IDs (e.g. `"ord-0001"` matches `"ORD-0001"`).
- [x] Register `get_order_status` as a tool in `assets/commerce-order-assistant-agent/app/agent.py` using the `@tool` decorator pattern from the bootstrap template.
- [x] Ensure the tool description clearly states: "Look up the status and estimated delivery date for a given order ID. Returns order details if found, or a not-found result if the order ID does not exist."

### System Prompt & Agent Behaviour

- [x] Open `assets/commerce-order-assistant-agent/app/agent.py` and configure the system prompt (`@prompt_section` / `get_system_prompt`) with the following instructions:
  - The agent's name is **CommerceOrderAssistant**.
  - Its purpose is to help e-commerce customers check the status and estimated delivery date of their orders.
  - **Inquiry Understanding (M1)**: When a customer asks about an order (in any phrasing), identify it as an order-tracking request.
  - **Order ID Collection (M2)**: If the customer has not provided an order ID, politely ask for it. If the customer's reply does not contain a recognizable order ID, ask again clearly — do not enter an error state.
  - **Order Data Retrieval (M3)**: Once an order ID is available, call the `get_order_status` tool with that order ID.
  - **Status Response (M4)**: If the tool returns a found order, respond with the order status and estimated delivery date in plain, friendly language. Do not expose raw JSON or technical fields.
  - **Edge Case — Unknown Order (M5a)**: If the tool returns `found: false`, inform the customer clearly that the order ID was not found and suggest they verify their order ID or contact support.
  - **Edge Case — Missing Order ID (M5b)**: If the customer repeatedly does not provide an order ID, offer a helpful prompt (e.g., "Your order ID can be found in your confirmation email, usually formatted as ORD-XXXX.").
  - The agent must NEVER fabricate order data. It MUST always use the `get_order_status` tool for order information.
  - The agent handles order status and delivery inquiries only. For requests about cancellations, returns, or modifications, politely state that these are outside its current scope and suggest contacting customer support.
- [x] Set the agent's display name and description in `assets/commerce-order-assistant-agent/app/agent.py` to:
  - Name: `CommerceOrderAssistant`
  - Description: `AI-powered self-service agent for e-commerce order tracking. Provides order status and estimated delivery dates from simulated order data.`

### Input Validation & Guardrails

- [x] Ensure the agent never modifies any order data — `get_order_status` is strictly read-only.
- [x] Ensure no personally identifiable information (PII) is logged, stored, or included in responses.
- [x] If the customer's message is entirely unrelated to order tracking (e.g., a request for product recommendations or a complaint about a product), the agent should acknowledge the message, state its scope, and suggest the appropriate support channel.

---

## Business Instrumentation

- [x] Implement business step instrumentation for each milestone from the PRD using structured logging and OpenTelemetry custom spans. See [guidelines-agent-python.md](../guidelines-agent-python.md) for the Python-specific implementation pattern. Extract business logic from `stream()` into a plain async helper to avoid `GeneratorExit` context errors.

  Milestones to instrument:

  | ID | Name | Log on achievement | Log on miss |
  |----|------|--------------------|-------------|
  | M1 | Inquiry Understanding | `M1.achieved: order tracking intent identified from customer message` | `M1.missed: could not identify order tracking intent from customer message` |
  | M2 | Order ID Collection | `M2.achieved: order ID collected from customer input` | `M2.missed: order ID not provided or not recognized after prompt` |
  | M3 | Order Data Retrieval | `M3.achieved: order data retrieved successfully from mock tool` | `M3.missed: mock tool call failed or returned an unexpected result` |
  | M4 | Status Response | `M4.achieved: order status and delivery date communicated to customer` | `M4.missed: failed to generate or deliver order status response` |
  | M5 | Edge Case Handling | `M5.achieved: edge case handled gracefully (unknown or missing order ID)` | `M5.missed: edge case resulted in unhandled error or unhelpful response` |

- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

> No external SAP API or MCP server integration is required for this agent. All order data is provided by the built-in `get_order_status` mock tool. Skip all MCP server discovery, translation, and wiring tasks.

- [x] Confirm `asset.yaml` does NOT include any `requires` entries for MCP servers (no external dependencies).
- [x] Confirm no `mcp-translation-file` invocation is needed.
- [x] Confirm no `mcp-mock.json` generation is needed (no MCP servers to mock).

---

## Testing

> See [guidelines-agent-python.md](../guidelines-agent-python.md) for Python testing setup and patterns.

- [x] `conftest.py` only sets `IBD_TESTING=true`
- [x] Write unit tests in `assets/commerce-order-assistant-agent/tests/`:
  - `test_order_lookup_tool.py`: Tests for `get_order_status`:
    - Returns correct order data for a known order ID
    - Returns `found: false` for an unknown order ID
    - Matches order IDs case-insensitively
    - Returns all required fields (`order_id`, `status`, `estimated_delivery_date`, `item_description`) for a found order
  - `test_agent_server.py`: Test that the agent starts and exposes `/.well-known/agent.json` with correct name and description
- [x] Write one integration test in `assets/commerce-order-assistant-agent/tests/test_integration.py` executing the end-to-end agent flow with mocked LLM responses:
  - Scenario 1: Customer asks "Where is my order ORD-0001?" → agent returns order status and delivery date
  - Scenario 2: Customer asks "Track my order" (no ID) → agent prompts for order ID → customer provides "ORD-0005" → agent returns result
  - Scenario 3: Customer provides an unknown order ID → agent returns a not-found message
- [x] Run `pytest` from `assets/commerce-order-assistant-agent/` (no args) — if coverage < 70%, add tests until threshold met
- [x] Run `pytest` again from `assets/commerce-order-assistant-agent/` (no args) to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/commerce-order-assistant-agent/`
