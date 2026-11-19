# CommerceOrderAssistant

AI-powered e-commerce customer support agent for order tracking

## Business challenge

E-commerce customers frequently contact support teams to check their order status and estimated delivery dates because order information is not always easy to access. This leads to longer response times, repetitive manual work for customer support representatives, and poor customer satisfaction.

The goal is to build CommerceOrderAssistant — an AI-powered customer support agent that understands order-tracking questions, requests an order ID, retrieves order details from an approved mock order data source, and provides accurate order status and estimated delivery information.

Primary users are e-commerce customers; customer support teams benefit from reduced repetitive inquiries. The project uses simulated order data without accessing real customer information.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Order-status-related support tickets | — | Reduce by 40% | 30-day simulated period | Customer Order Self-Service | user |
| Response time for valid order inquiries | — | 95% answered within 10 seconds | 30-day simulated period | Order Status Retrieval | user |
| Accuracy of order status responses | — | ≥ 95% accuracy from mock data | 30-day simulated period | Order Data Lookup | user |
| Self-service resolution rate | — | ≥ 90% without human intervention | 30-day simulated period | Customer Support Deflection | user |
| Handling of edge cases (missing ID / unknown order) | — | 100% success in predefined test cases | Current practice session | Order Inquiry Validation | user |

## Key Milestones

1. **Inquiry Understanding** — Agent successfully interprets a natural language order-tracking question from a customer.
2. **Order ID Collection** — Agent requests and validates the order ID from the user when not provided.
3. **Order Data Retrieval** — Agent calls the mock order lookup tool and retrieves order details by ID.
4. **Status Response** — Agent returns accurate order status and estimated delivery date to the customer.
5. **Edge Case Handling** — Agent gracefully handles unknown order IDs and missing order ID inputs with clear, helpful responses.

## Business Architecture (RBA)

### End-to-End Process

Lead to Cash (generic)

### Process Hierarchy

```
Lead to Cash (E2E)
└── Order to Fulfill (Phase)
    └── Manage customer orders and contracts (BPS-361)
        └── Manage customer orders
```

### Summary

The challenge maps to the Lead to Cash E2E, specifically the Order to Fulfill phase where customers need visibility into order status and delivery timelines. The AI agent addresses the customer-facing side of order monitoring, reducing inbound support load by enabling self-service inquiries.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
|------------------------|-------------------------|------------|-------------------|--------------------|--------------------|---------------------|------|---------------------|
| Retrieve order status and delivery date | SAP Commerce Cloud — Distributed Order Orchestration; SAP Order Management Foundation — Customer Order Monitoring | — | — | — | — | — | Yes | All discovered APIs are unavailable in this landscape; mock order data tool will be used |
| Natural language order inquiry handling | No standard SAP asset | — | — | — | — | — | Yes | Custom AI agent built to handle NLP order queries |
| Edge case handling (missing/unknown order ID) | No standard SAP asset | — | — | — | — | — | Yes | Custom agent logic required for validation and error responses |

### Key findings

- All relevant SAP order management APIs (Order Tracking, Customer Service, Orders) are unavailable in this landscape — a custom mock order lookup tool is required.
- No MCP servers are available for order management in this environment; the agent will use a built-in Python tool.
- SAP Commerce Cloud and SAP Order Management Foundation cover the standard business process but are not accessible for this practice project.
- The solution is self-contained: a Python AI agent with a mock data tool, no external system integration needed.
- This is a practice/certification project — targets are simulated over a hypothetical 30-day period.

## Recommendations

### CommerceOrderAssistant — AI Agent for Order Tracking

#### Executive Summary

Python AI agent with mock order lookup tool for self-service order tracking.

#### Recommended Solution

Build a pro-code Python AI agent (A2A protocol) named CommerceOrderAssistant. The agent:
- Accepts natural language order-tracking questions from customers
- Requests an order ID when not provided by the customer
- Calls a custom mock order lookup tool that returns order status and estimated delivery date from simulated data
- Handles edge cases: unknown order IDs and missing order IDs, with clear and helpful responses
- Is instrumented with OpenTelemetry for business step visibility across key milestones

No live SAP system integration is required. All order data is served from a mock in-memory dataset built into the agent.

#### Problem Statement

E-commerce customers repeatedly contact human support agents for routine order status questions. This creates high volumes of repetitive inquiries, increases support costs, and degrades customer experience due to wait times. An AI agent can deflect these inquiries with instant, accurate self-service responses.

#### Affected User Roles

- E-commerce customers — primary users who ask order-tracking questions
- Customer support representatives — benefit from reduced repetitive inbound inquiries

#### Important factors

##### Reduces manual effort through automation
The agent eliminates the need for support agents to manually look up and communicate order status, freeing them for higher-value interactions.

##### Self-service customer experience
Customers receive instant, accurate order information without waiting for a human agent, improving satisfaction and reducing friction.

##### Mock data enables safe practice
Using simulated order data ensures no real customer information (PII) is processed, making this appropriate for a learning and certification context.

#### Potential risks

##### Mock data does not reflect production complexity
Real order data may have more states, edge cases, and integration points than the mock. The agent will need to be extended for production use.

##### Scope limited to order tracking
The agent handles only order status and delivery date inquiries. Requests for cancellations, returns, or modifications are out of scope.

#### Recommended solution category

AI Agent

#### Intent fit
92%
