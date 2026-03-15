import os
import httpx
from langchain_core.tools import tool


@tool
async def serper_search(query: str) -> str:
    """Search Google using Serper API. Use this to find market data, competitor info, news, and trends."""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "Error: SERPER_API_KEY not set"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": query, "num": 10},
        )
        response.raise_for_status()
        data = response.json()

    results = []
    for item in data.get("organic", [])[:8]:
        results.append(
            f"**{item.get('title', '')}**\n"
            f"URL: {item.get('link', '')}\n"
            f"{item.get('snippet', '')}\n"
        )

    if data.get("knowledgeGraph"):
        kg = data["knowledgeGraph"]
        results.insert(
            0,
            f"**Knowledge Graph: {kg.get('title', '')}**\n"
            f"{kg.get('description', '')}\n",
        )

    return "\n---\n".join(results) if results else "No results found."


@tool
async def firecrawl_scrape(url: str) -> str:
    """Scrape a webpage and return its content as markdown. Use this to get detailed information from specific URLs."""
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        return "Error: FIRECRAWL_API_KEY not set"

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"url": url, "formats": ["markdown"]},
        )
        response.raise_for_status()
        data = response.json()

    if not data.get("success"):
        return f"Failed to scrape {url}"

    markdown = data.get("data", {}).get("markdown", "")
    # Truncate to avoid overwhelming the LLM
    if len(markdown) > 8000:
        markdown = markdown[:8000] + "\n\n... [content truncated]"

    return markdown if markdown else f"No content extracted from {url}"
