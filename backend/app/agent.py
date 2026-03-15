import json
import os
from typing import AsyncGenerator

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from app.tools import serper_search, firecrawl_scrape

SYSTEM_PROMPT = """You are a Growth Intelligence Research Agent. Your job is to research and analyze strategic growth questions for product teams.

When given a query, you should:
1. Break down the question into research angles
2. Use the available tools to gather real data:
   - Use serper_search to find market data, competitor information, news, and trends
   - Use firecrawl_scrape to get detailed content from specific URLs you find interesting
3. Synthesize your findings into actionable intelligence

Guidelines:
- Always ground your analysis in real data from your research
- Clearly distinguish between facts (sourced data) and your interpretations
- Provide confidence levels (high/medium/low) for your conclusions
- Include source URLs for key claims
- Be concise but thorough - focus on actionable insights
- Structure your response with clear sections"""


def _build_agent():
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=4096,
    )
    tools = [serper_search, firecrawl_scrape]
    return create_react_agent(llm, tools)


async def run_agent(query: str, conversation_history: list[dict] | None = None) -> AsyncGenerator[str, None]:
    """Run the research agent and yield SSE event strings."""
    agent = _build_agent()

    # Build message list
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    if conversation_history:
        for msg in conversation_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=query))

    # Emit initial status
    yield _sse_event("agent_status", {
        "agent_id": "research_agent",
        "status": "spawned",
        "message": "Starting research...",
    })

    yield _sse_event("agent_status", {
        "agent_id": "research_agent",
        "status": "researching",
        "message": "Analyzing query and planning research...",
    })

    try:
        final_content = ""
        seen_tools = set()

        async for event in agent.astream_events(
            {"messages": messages},
            version="v2",
        ):
            kind = event.get("event")

            # Detect tool calls
            if kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "tool_call_chunks"):
                    for tc in chunk.tool_call_chunks:
                        if tc.get("name") and tc["name"] not in seen_tools:
                            seen_tools.add(tc["name"])
                            tool_name = tc["name"]
                            if tool_name == "serper_search":
                                msg = "Searching the web..."
                            elif tool_name == "firecrawl_scrape":
                                msg = "Scraping webpage for details..."
                            else:
                                msg = f"Using {tool_name}..."
                            yield _sse_event("agent_status", {
                                "agent_id": "research_agent",
                                "status": "researching",
                                "message": msg,
                            })

            # Detect tool results
            if kind == "on_tool_end":
                tool_name = event.get("name", "")
                output = event.get("data", {}).get("output", "")
                snippet = str(output)[:300]
                yield _sse_event("finding", {
                    "agent_id": "research_agent",
                    "domain": "Research",
                    "finding": f"[{tool_name}] {snippet}...",
                })

            # Capture final AI message
            if kind == "on_chat_model_end":
                output = event.get("data", {}).get("output")
                if output and hasattr(output, "content") and isinstance(output.content, str):
                    final_content = output.content

        # Emit synthesis
        if final_content:
            yield _sse_event("agent_status", {
                "agent_id": "research_agent",
                "status": "complete",
                "message": "Research complete",
            })
            yield _sse_event("synthesis", {
                "summary": final_content,
                "confidence": "medium",
                "sources_count": len(seen_tools),
            })
        else:
            yield _sse_event("error", {
                "message": "Agent produced no output",
            })

    except Exception as e:
        yield _sse_event("agent_status", {
            "agent_id": "research_agent",
            "status": "failed",
            "message": str(e),
        })
        yield _sse_event("error", {
            "message": f"Agent error: {str(e)}",
        })

    yield _sse_event("done", {})


def _sse_event(event_type: str, data: dict) -> str:
    """Format an SSE event as a JSON string."""
    return json.dumps({"event": event_type, "data": data})
