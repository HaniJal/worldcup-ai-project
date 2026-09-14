"""Live web search tool, backed by Tavily. Used by the agent for questions
outside the scope of the seeded dataset (e.g. things not captured in the
DB or the RAG knowledge base)."""

from src.settings import settings


def web_search(query: str, max_results: int = 5) -> list[dict]:
    if not settings.TAVILY_API_KEY:
        return [{"error": "TAVILY_API_KEY is not set. Add it to .env to enable web search."}]

    # Imported lazily so the package is only required if this tool is used.
    from tavily import TavilyClient

    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    response = client.search(query=query, max_results=max_results, search_depth="basic")

    return [
        {
            "title": r.get("title"),
            "url": r.get("url"),
            "content": r.get("content"),
        }
        for r in response.get("results", [])
    ]
