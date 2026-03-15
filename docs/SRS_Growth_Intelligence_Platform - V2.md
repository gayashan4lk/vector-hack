# Software Requirements Specification (SRS)

## Growth Intelligence Platform — Multi-Agent Conversational System

**Version:** 2.0
**Date:** 15 March 2026
**Event:** Veracity AI × Hatch Hackathon
**Build Window:** 3 Hours
**Architecture:** Split — Next.js Frontend + FastAPI/LangGraph Backend

---

## 1. Introduction

### 1.1 Purpose

This document defines the software requirements for a multi-agent conversational intelligence platform that delivers real-time growth intelligence to product teams through a single chat interface. The system replaces the manual process of synthesising insights from 16+ tools by orchestrating specialised AI agents that research, analyse, and present findings as interactive inline artifacts.

### 1.2 Scope

The application is a web-based conversational interface backed by a multi-agent orchestration engine. A user asks a strategic growth question in natural language. The system decomposes the question, dispatches parallel research agents across live data sources, synthesises findings with confidence scoring, and renders results as interactive UI components within the conversation thread.

### 1.3 Target Users

- Product managers evaluating market positioning
- Growth teams assessing competitive landscape
- Strategy leads preparing board-level intelligence briefs

### 1.4 Constraints

- 3-hour build window — prioritise working demo over feature completeness
- Free-tier APIs only — no paid subscriptions required
- Must demonstrate against Vector Agents (vectoragents.ai) and generalise to at least one other product
- Must show agent coordination, not a single prompt-response wrapper

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND — Next.js 14 + Tailwind                │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │ Chat Input   │  │ Agent Status │  │ Inline Artifacts   │  │
│  │ & Thread     │  │ Panel (Live) │  │ (Recharts/Chart.js)│  │
│  └─────────────┘  └──────────────┘  └────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │ SSE Stream (HTTP)
                           │ POST /api/query
┌──────────────────────────▼──────────────────────────────────┐
│              BACKEND — FastAPI + LangGraph                    │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              LangGraph State Graph                      │  │
│  │                                                        │  │
│  │  ┌──────────────┐                                      │  │
│  │  │ ORCHESTRATOR │─── decomposes query ──┐              │  │
│  │  │    Node      │                       │              │  │
│  │  └──────────────┘                       ▼              │  │
│  │                              ┌─────────────────────┐   │  │
│  │                              │  PARALLEL FAN-OUT   │   │  │
│  │                              └──┬──┬──┬──┬──┬──┬───┘   │  │
│  │                                 │  │  │  │  │  │       │  │
│  │                                 ▼  ▼  ▼  ▼  ▼  ▼       │  │
│  │                     ┌──────┐┌──────┐┌──────┐┌──────┐   │  │
│  │                     │Market││Compet││Win/  ││Price │   │  │
│  │                     │Trend ││itive ││Loss  ││Intel │   │  │
│  │                     │Agent ││Agent ││Agent ││Agent │   │  │
│  │                     └──────┘└──────┘└──────┘└──────┘   │  │
│  │                     ┌──────┐┌──────┐                   │  │
│  │                     │Posit-││Adjac-│                   │  │
│  │                     │ioning││ent   │                   │  │
│  │                     │Agent ││Market│                   │  │
│  │                     └──┬───┘└──┬───┘                   │  │
│  │                        │      │                        │  │
│  │                        ▼      ▼                        │  │
│  │                  ┌──────────────────┐                  │  │
│  │                  │ SYNTHESIS NODE   │                  │  │
│  │                  │ Merge + Confidence│                 │  │
│  │                  └──────────────────┘                  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                    TOOL LAYER                           │  │
│  │  Firecrawl · SerpAPI · Meta Ad Library · Reddit API     │  │
│  │  HN Algolia · USPTO Patents · Playwright (fallback)     │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Layer | Technology | Justification |
|---|---|---|
| **Frontend** | Next.js 14 (App Router) + Tailwind CSS | Fast scaffolding, SSR, streaming SSE consumption |
| **Backend Framework** | FastAPI (Python 3.11+) | Native async, SSE via StreamingResponse, fast prototyping |
| **Agent Orchestration** | LangGraph (langgraph) | State-graph-based multi-agent orchestration with parallel fan-out, lifecycle hooks, built-in state management |
| **LLM Backbone** | Claude API via LangChain ChatAnthropic | Native tool calling, structured output, streaming |
| **Web Scraping** | Firecrawl Python SDK | 500 free credits, returns LLM-ready markdown |
| **Search Data** | SerpAPI (free tier) via langchain-community | Google Trends, News, Ads as structured JSON |
| **Ad Intelligence** | Meta Ad Library API | Free, structured JSON, political + EU ads |
| **Community Signal** | Reddit API (OAuth2) + HN Algolia | Free, real user voice and developer sentiment |
| **Fallback Scraper** | Playwright (Python) | For JS-heavy sites with no API |
| **Streaming** | Server-Sent Events (SSE) | Real-time agent status and response streaming |
| **Communication** | HTTP — `POST /api/query` → SSE stream | Single endpoint, frontend consumes EventSource |

### 2.3 Architecture Decision: Why Split Stack

The split architecture (Next.js + FastAPI) is chosen over a monolithic Next.js approach for the following reasons:

1. **LangGraph is Python-first** — the multi-agent state graph, parallel fan-out, and lifecycle management features are mature and well-documented in Python. The JS/TS port lags behind.
2. **LangChain tool ecosystem** — SerpAPI, Firecrawl, Reddit, and other tool wrappers are production-ready in Python with more examples and fewer edge-case bugs.
3. **Hackathon risk reduction** — debugging obscure JS agent issues under time pressure is a project-killer. Python LangGraph has more community support and examples for the exact pattern we need.
4. **Clean separation** — frontend team can work on UI/artifacts independently while backend team builds the agent graph. The SSE contract is the only integration point.

### 2.4 Key Python Dependencies

```
fastapi>=0.110.0
uvicorn>=0.29.0
sse-starlette>=2.0.0
langchain>=0.2.0
langchain-anthropic>=0.1.0
langchain-community>=0.2.0
langgraph>=0.1.0
firecrawl-py>=1.0.0
httpx>=0.27.0
pydantic>=2.0.0
playwright>=1.40.0  # fallback scraper
python-dotenv>=1.0.0
```

### 2.5 Key Frontend Dependencies

```
next@14
react@18
tailwindcss@3
recharts  # inline charts
lucide-react  # icons
```

---

### 2.6 LangGraph State Graph Design

```python
# Conceptual graph structure

class AgentState(TypedDict):
    query: str                          # Original user question
    conversation_history: list          # Prior messages for memory
    decomposed_tasks: list[dict]        # Orchestrator output
    agent_findings: dict[str, dict]     # Results keyed by agent_id
    agent_statuses: dict[str, str]      # Lifecycle states
    synthesis: dict                     # Final merged output
    artifacts: list[dict]               # Renderable artifact payloads

# Graph flow:
# START → orchestrator_node → conditional_fan_out
#              ├─→ market_trend_agent ──────┐
#              ├─→ competitive_agent ───────┤
#              ├─→ win_loss_agent ──────────┤
#              ├─→ pricing_agent ───────────┤──→ synthesis_node → END
#              ├─→ positioning_agent ───────┤
#              └─→ adjacent_market_agent ───┘
```

### 2.7 API Contract

**Endpoint:** `POST /api/query`

**Request Body:**

```json
{
  "query": "Is Vector Agents competitive in the AI SDR market?",
  "conversation_history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

**Response:** SSE stream (`text/event-stream`) with the following event types:

| Event Type | Payload | When Emitted |
|---|---|---|
| `agent_status` | `{agent_id, status, message}` | Each agent lifecycle transition |
| `finding` | `{agent_id, domain, finding}` | As each agent completes a research step |
| `artifact` | `{type, title, payload}` | When a renderable artifact is ready |
| `synthesis` | `{summary, confidence, sources_count}` | After all agents merge |
| `error` | `{agent_id, message}` | On agent failure |
| `done` | `{}` | Stream complete |

## 3. Functional Requirements

### 3.1 Conversational Interface (FR-01)

**FR-01.1** — The system shall provide a single-page chat interface where the user types natural language questions.

**FR-01.2** — The system shall display streamed responses in real time as agents complete their work.

**FR-01.3** — The system shall maintain conversational memory within a session — follow-up questions build on prior context.

**FR-01.4** — The system shall offer pre-built "starter" query chips for demo convenience:
- "Is Vector Agents competitive in the AI SDR market right now?"
- "Is the digital workers category accelerating or consolidating?"
- "What should Vector Agents build or reposition over the next six months?"

### 3.2 Query Decomposition & Orchestration (FR-02)

**FR-02.1** — The Orchestrator Agent shall receive the user's question and decompose it into sub-tasks mapped to one or more of the six intelligence domains:

| Domain | Agent Responsibility |
|---|---|
| Market & Trend Sensing | Category trajectory, leading indicators, search trends |
| Competitive Landscape | Competitor identification, feature comparison, funding signals |
| Win/Loss Intelligence | Review sentiment, buyer objections, churn signals |
| Pricing & Packaging | Pricing model analysis, willingness-to-pay signals |
| Positioning & Messaging | How competitors talk about themselves vs. user perception |
| Adjacent Market Collision | Threats from outside the core category |

**FR-02.2** — The Orchestrator shall dispatch relevant specialist agents in parallel using LangGraph's `Send()` API for concurrent fan-out, not sequential execution.

**FR-02.3** — The Orchestrator shall track agent lifecycle states via LangGraph state: `spawned → researching → synthesising → complete → failed`. Each state transition emits an SSE event to the frontend.

**FR-02.4** — The Orchestrator shall handle agent failure gracefully — LangGraph's conditional edges route around failed agents, and the system still returns partial results with a note about the gap.

### 3.3 Specialist Agents (FR-03)

Each specialist agent shall:

**FR-03.1** — Execute one or more tool calls to retrieve live data from external sources.

**FR-03.2** — Perform multi-hop research where needed — initial search → deepen promising leads → cross-reference → surface findings.

**FR-03.3** — Return structured output in the following schema:

```json
{
  "agent_id": "market_trend_agent",
  "domain": "Market & Trend Sensing",
  "status": "complete",
  "confidence": "high | medium | low",
  "findings": [
    {
      "type": "fact | interpretation",
      "claim": "The AI SDR market grew 40% YoY in 2025.",
      "source": "https://example.com/report",
      "confidence": "high",
      "retrieved_at": "2026-03-15T10:23:00Z"
    }
  ],
  "summary": "Short synthesis paragraph."
}
```

**FR-03.4** — Clearly separate facts (sourced data points) from interpretations (agent-generated analysis).

### 3.4 Data Source Integration (FR-04)

**FR-04.1 — Firecrawl (Primary)**
- Scrape any URL to LLM-ready markdown
- Use for competitor product pages, blog posts, documentation
- 500 free credits available

**FR-04.2 — SerpAPI**
- Google Search, Google Trends, Google News
- 100 free searches/month
- Use for market signals, trend data, news mentions

**FR-04.3 — Meta Ad Library API**
- Competitor ad creatives, spend ranges, demographics
- Free with identity verification
- Use for positioning and messaging analysis

**FR-04.4 — Reddit API (OAuth2)**
- Subreddit search for product mentions, complaints, praise
- Free tier sufficient
- Use for win/loss intelligence and user sentiment

**FR-04.5 — HN Algolia API**
- Search Hacker News posts and comments
- Free, no API key required
- Use for developer sentiment and tech community buzz

**FR-04.6 — Playwright (Fallback)**
- Browser automation for JS-heavy sites without APIs
- Use for BigSpy, Google Ads Transparency, LinkedIn Ad Library

### 3.5 Inline Artifact Rendering (FR-05)

**FR-05.1** — The system shall render findings as interactive UI components inside the chat thread, not as plain text or external links.

**FR-05.2** — Required artifact types:

| Artifact | Use Case | Minimum Implementation |
|---|---|---|
| Competitive Landscape Map | Show players, positioning, funding | Interactive card grid or bubble chart |
| Trend Chart | Category growth, search interest over time | Line/area chart (Recharts or Chart.js) |
| Pricing Comparison Table | Side-by-side pricing tiers | Sortable/filterable table |
| Sentiment Scorecard | Win/loss signals from reviews & forums | Colour-coded score cards with source links |
| Messaging Gap Matrix | Positioning vs. perception alignment | Heatmap or comparison matrix |
| Source Trail Panel | All sources with confidence badges | Expandable list with timestamps |

**FR-05.3** — Each artifact shall be interactive — at minimum, clickable to expand or drill down.

**FR-05.4** — Each artifact shall display a confidence indicator (high/medium/low) and link to underlying sources.

### 3.6 Agent Status Visibility (FR-06)

**FR-06.1** — The UI shall display a real-time panel showing which agents are active, their current state, and what data source they are querying.

**FR-06.2** — Status updates shall stream to the frontend via SSE as agents progress through lifecycle states.

**FR-06.3** — Completed agents shall show a summary chip that can be expanded for detail.

### 3.7 Conversational Memory (FR-07)

**FR-07.1** — The system shall maintain a session-level conversation history.

**FR-07.2** — Follow-up queries shall have access to all prior findings — the user should not need to re-explain context.

**FR-07.3** — New research results shall update prior conclusions when contradictory evidence is found.

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-01** — First visible agent status update shall appear within 3 seconds of query submission.

**NFR-02** — Full synthesis response shall complete within 60–90 seconds for a standard query.

**NFR-03** — Parallel agent execution shall reduce total time compared to sequential execution by at least 50%.

### 4.2 Reliability

**NFR-04** — The system shall degrade gracefully — a failed data source shall not crash the entire response.

**NFR-05** — Each agent shall have a 30-second timeout with automatic fallback messaging.

### 4.3 Scalability Considerations

**NFR-06** — The architecture shall document a path to horizontal scaling (e.g., agent workers as serverless functions).

**NFR-07** — The system shall estimate and display cost-per-query (LLM tokens + API calls) for GTM viability.

### 4.4 Security

**NFR-08** — API keys shall be stored as environment variables, never hardcoded or exposed to the client.

**NFR-09** — All external API calls shall be made server-side only.

---

## 5. Build Plan — 3-Hour Sprint

### Team Split Strategy

If working in a team, split into two parallel tracks after Phase 1 setup:

- **Track A (Backend):** FastAPI + LangGraph agent graph — Phases 2A and 3A
- **Track B (Frontend):** Next.js chat UI + artifact components — Phases 2B and 3B

Integration point: SSE event contract (defined in Phase 1).

### Phase 1: Foundation & Contract (0:00 – 0:40)

| Task | Owner | Time | Output |
|---|---|---|---|
| FastAPI scaffold + `/api/query` SSE endpoint | Backend | 10 min | Running FastAPI server with streaming |
| Next.js scaffold + Tailwind + chat UI shell | Frontend | 15 min | Running dev server with input box and message thread |
| Define SSE event contract (JSON schema for agent status, findings, artifacts) | Both | 10 min | Shared interface document |
| Wire frontend EventSource to backend SSE endpoint (hello world test) | Both | 5 min | End-to-end stream confirmed |

**SSE Event Contract:**

```json
// Agent status event
{"event": "agent_status", "data": {"agent_id": "market_trend", "status": "researching", "message": "Searching Google Trends..."}}

// Finding event (partial result)
{"event": "finding", "data": {"agent_id": "competitive", "domain": "Competitive Landscape", "finding": {...}}}

// Artifact event (rendered component)
{"event": "artifact", "data": {"type": "competitive_table | trend_chart | pricing_table | scorecard | heatmap | source_trail", "payload": {...}}}

// Synthesis event (final summary)
{"event": "synthesis", "data": {"summary": "...", "confidence": "high", "sources_count": 12}}

// Done event
{"event": "done", "data": {}}
```

### Phase 2: Agent Engine + Chat UI (0:40 – 1:40)

**Track A — Backend (Agent Engine)**

| Task | Time | Output |
|---|---|---|
| LangGraph state schema — define AgentState with messages, findings, agent_statuses | 10 min | Typed state object |
| Orchestrator node — Claude call that decomposes query into domain sub-tasks | 15 min | Routes questions to relevant agents |
| Tool definitions — Firecrawl scrape, SerpAPI search, HN Algolia search, Reddit search | 15 min | LangChain tools callable by agents |
| Specialist agent nodes (6x) — each with domain-specific system prompt + tools | 15 min | Individual agent nodes |
| Parallel fan-out — LangGraph `Send()` API to dispatch agents concurrently | 5 min | Agents run in parallel |

**Track B — Frontend (Chat UI)**

| Task | Time | Output |
|---|---|---|
| Chat message components — user bubble, assistant bubble, streaming text | 15 min | Functional chat thread |
| SSE consumer hook — `useEventSource` that parses agent_status, finding, artifact, synthesis events | 15 min | Real-time event handling |
| Agent status panel component — shows agent names, states, spinners | 15 min | Live agent visibility |
| Starter query chips — clickable pre-built questions | 5 min | Demo-ready entry point |
| Session memory — store conversation history in React state, send with each query | 10 min | Follow-up queries work |

### Phase 3: Synthesis + Artifacts (1:40 – 2:25)

**Track A — Backend (Synthesis)**

| Task | Time | Output |
|---|---|---|
| Synthesis node — merge all agent findings, assign overall confidence, generate summary | 15 min | Unified intelligence brief |
| Artifact payload generation — structure findings into renderable artifact JSON | 15 min | Frontend-ready artifact payloads |
| SSE emission — stream agent_status, finding, artifact, synthesis events as agents complete | 15 min | Real-time backend → frontend pipeline |

**Track B — Frontend (Artifacts)**

| Task | Time | Output |
|---|---|---|
| Competitive landscape artifact — card grid or table with player details | 15 min | Inline competitive view |
| Trend chart artifact — Recharts line/area chart for market signals | 10 min | Inline trend visualisation |
| Scorecard artifact — confidence-scored finding cards with source links | 10 min | Inline intelligence cards |
| Source trail panel — expandable list of all sources with confidence badges | 10 min | Transparency layer |

### Phase 4: Polish & Demo Prep (2:25 – 3:00)

| Task | Owner | Time | Output |
|---|---|---|---|
| Error handling — agent timeouts, API failures, graceful degradation | Backend | 10 min | Robust demo |
| Loading states, animations, empty states | Frontend | 10 min | Polished UX |
| Test with Vector Agents demo queries | Both | 5 min | Validated primary demo |
| Test generalisation with second product (e.g., Notion, Linear, or a fintech) | Both | 5 min | Proves generalisability |
| Final demo run-through — rehearse 10-minute narrative | Both | 5 min | Demo-ready |

---

## 6. Demo Script

### Demo Flow (10 minutes)

**Opening (1 min):** Briefly state the problem — growth intelligence takes weeks, scattered across 16+ tools.

**Live Query 1 (3 min):** Type "Is Vector Agents competitive in the AI SDR market right now?" Show agents spinning up, data flowing in, and the competitive landscape artifact rendering inline.

**Live Query 2 (2 min):** Follow up with "What should Vector Agents build or reposition over the next six months?" Show conversational memory in action — no re-explanation needed.

**Generalisation (2 min):** Switch to a different product entirely (e.g., a fintech or e-commerce tool) and ask a growth question. Show the system works beyond Vector Agents.

**Architecture Walkthrough (2 min):** Briefly show the agent status panel, explain the multi-agent coordination, point out confidence scoring and source trails. Emphasise that this is not a single LLM call.

---

## 7. Evaluation Alignment

| Criterion (Weight) | How This SRS Addresses It |
|---|---|
| Core Algorithm — Multi-Agent System (25%) | LangGraph state graph with 6 specialist agent nodes + orchestrator + synthesis node, parallel fan-out via Send(), lifecycle state tracking, LangChain tool integrations |
| Product Design Strategy (25%) | Inline interactive artifacts (Recharts charts, card grids, scorecards), real-time agent status panel, starter chips, SSE streaming UX |
| Intelligence Quality & Grounding (20%) | Multi-source data via Firecrawl/SerpAPI/Reddit/HN, confidence scores on every finding, fact vs. interpretation separation, source trail panel |
| Scalability & Cost Efficiency (15%) | FastAPI async backend (serverless-deployable), LangGraph graph is horizontally scalable, cost-per-query estimation, free-tier APIs |
| Demo Strength & Generalisability (15%) | Scripted demo with Vector Agents + second product, conversational memory via state, visible agent coordination |

---

## 8. Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| API rate limits hit during demo | Agent returns no data | Cache demo queries; implement graceful fallback messaging |
| Firecrawl credits exhausted | Cannot scrape live pages | Pre-cache key URLs; use Playwright as backup |
| Claude API latency spikes | Slow response times | Stream partial results; show agent progress to maintain engagement |
| Agent returns hallucinated data | Low intelligence quality | Enforce structured output schema; validate all claims have source URLs |
| 3-hour time overrun | Incomplete features | Build in priority order — Phase 1 & 2 are non-negotiable; Phase 3 & 4 are enhancers |
| CORS issues between Next.js and FastAPI | Frontend cannot reach backend | Configure FastAPI CORSMiddleware in Phase 1; test immediately |
| LangGraph parallel execution errors | Agents crash silently | Wrap each agent node in try/except; emit error SSE event on failure |
| Python dependency conflicts | Backend won't start | Use a clean venv; pin all versions in requirements.txt |
| SSE connection drops mid-stream | Frontend shows incomplete results | Implement reconnection logic in frontend EventSource hook; show "reconnecting" state |

---

## 9. Glossary

| Term | Definition |
|---|---|
| Agent | An autonomous LLM-powered unit with a specific research scope and set of tools |
| Artifact | An interactive UI component rendered inline within the conversation |
| Confidence Score | A rating (high/medium/low) indicating the reliability of a finding |
| FastAPI | A modern Python web framework with native async support, used for the backend |
| Intelligence Domain | One of the six strategic areas the system must cover |
| LangGraph | A Python library for building stateful, multi-agent workflows as directed graphs with parallel execution |
| LangChain | A framework for building LLM-powered applications with standardised tool and model interfaces |
| MCP | Model Context Protocol — allows Claude to directly use external tools like Firecrawl |
| Multi-hop Research | A research pattern where initial findings lead to deeper follow-up queries |
| Orchestrator | The central agent node that decomposes queries and routes to specialist agent nodes |
| Send() | LangGraph's API for dispatching parallel agent execution (fan-out pattern) |
| SSE | Server-Sent Events — a protocol for streaming real-time updates from server to client |
| State Graph | LangGraph's core abstraction — a directed graph where nodes are agents/functions and edges define control flow |

---

*End of SRS — Version 2.0 (Updated: FastAPI + LangGraph Backend)*
