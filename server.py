# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp[cli]>=1.0.0", "httpx>=0.27.0"]
# ///
"""
ChipsNews MCP Server - Manage news.chipsbuilder.com via MCP.

Tools: config, sources CRUD, articles list/approve/reject, fetch trigger, stats.
Auth: API key (Bearer token).
"""

import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# --- Config from env ---
API_URL = os.environ.get("CHIPSNEWS_API_URL", "https://news.chipsbuilder.com").rstrip("/")
API_KEY = os.environ.get("CHIPSNEWS_API_KEY", "")

mcp = FastMCP(
    "chipsnews",
    instructions=(
        "ChipsNews MCP Server for AI-powered news aggregation. "
        "Manage news configuration, sources, articles, and fetch triggers "
        "via the ChipsFeed REST API at news.chipsbuilder.com."
    ),
)


# --- HTTP helper ---
async def api_request(
    method: str,
    path: str,
    *,
    json_data: dict | None = None,
    params: dict | None = None,
) -> dict | list | str:
    """Make an authenticated request to the ChipsNews API."""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    url = f"{API_URL}/api/v1{path}"

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.request(method, url, headers=headers, json=json_data, params=params)
        r.raise_for_status()
        if r.headers.get("content-type", "").startswith("application/json"):
            return r.json()
        return r.text


# ===== Configuration =====

@mcp.tool()
async def get_config() -> dict:
    """Get the news configuration (keywords, language, frequency, etc.)."""
    return await api_request("GET", "/config/")


@mcp.tool()
async def update_config(
    keywords: list[str] | None = None,
    language: str | None = None,
    frequency: str | None = None,
    auto_publish: bool | None = None,
    max_articles_per_fetch: int | None = None,
    use_google_news_fallback: bool | None = None,
    active: bool | None = None,
    notification_email: str | None = None,
    pin_duration_hours: int | None = None,
) -> dict:
    """Update news configuration. Only provided fields are updated.

    Args:
        keywords: List of keywords to track (e.g. ["AI", "startup", "tech"])
        language: Language code: en, it, de, fr, es
        frequency: Fetch frequency: 1h, 6h, 12h, 24h
        auto_publish: Auto-publish fetched articles (True/False)
        max_articles_per_fetch: Max articles per fetch (1-30)
        use_google_news_fallback: Use Google News when no RSS sources configured
        active: Enable/disable news fetching
        notification_email: Email address for article notifications (sent when new articles are fetched)
        pin_duration_hours: How long a pinned (TOP) article stays on top, in hours (default 48)
    """
    data = {}
    if keywords is not None:
        data["keywords"] = keywords
    if language is not None:
        data["language"] = language
    if frequency is not None:
        data["frequency"] = frequency
    if auto_publish is not None:
        data["auto_publish"] = auto_publish
    if max_articles_per_fetch is not None:
        data["max_articles_per_fetch"] = max_articles_per_fetch
    if use_google_news_fallback is not None:
        data["use_google_news_fallback"] = use_google_news_fallback
    if active is not None:
        data["active"] = active
    if notification_email is not None:
        data["notification_email"] = notification_email
    if pin_duration_hours is not None:
        data["pin_duration_hours"] = pin_duration_hours
    return await api_request("PATCH", "/config/", json_data=data)


# ===== Sources =====

@mcp.tool()
async def list_sources() -> dict:
    """List all news sources."""
    return await api_request("GET", "/sources/")


@mcp.tool()
async def create_source(
    source_type: str,
    label: str,
    url: str = "",
    query: str = "",
) -> dict:
    """Create a new news source.

    Args:
        source_type: Type of source: rss, google, reddit
        label: Display name for the source
        url: URL for RSS feeds or Reddit subreddits
        query: Search query for Google News sources
    """
    data = {"source_type": source_type, "label": label, "url": url, "query": query}
    return await api_request("POST", "/sources/", json_data=data)


@mcp.tool()
async def update_source(
    source_id: int,
    label: str | None = None,
    url: str | None = None,
    query: str | None = None,
    active: bool | None = None,
) -> dict:
    """Update an existing news source.

    Args:
        source_id: ID of the source to update
        label: New display name
        url: New URL
        query: New search query
        active: Enable/disable the source
    """
    data = {}
    if label is not None:
        data["label"] = label
    if url is not None:
        data["url"] = url
    if query is not None:
        data["query"] = query
    if active is not None:
        data["active"] = active
    return await api_request("PATCH", f"/sources/{source_id}/", json_data=data)


@mcp.tool()
async def delete_source(source_id: int) -> str:
    """Delete a news source.

    Args:
        source_id: ID of the source to delete
    """
    await api_request("DELETE", f"/sources/{source_id}/")
    return f"Source {source_id} deleted"


# ===== Articles =====

@mcp.tool()
async def list_articles(
    status: str | None = None,
    keyword: str | None = None,
    source: str | None = None,
    page: int = 1,
) -> dict:
    """List news articles with optional filters.

    Args:
        status: Filter by status: draft, published, rejected
        keyword: Filter by matched keyword
        source: Filter by source name
        page: Page number for pagination
    """
    params = {"page": page}
    if status:
        params["status"] = status
    if keyword:
        params["keyword"] = keyword
    if source:
        params["source"] = source
    return await api_request("GET", "/articles/", params=params)


@mcp.tool()
async def get_article(article_id: int) -> dict:
    """Get full details of a single article.

    Args:
        article_id: ID of the article
    """
    return await api_request("GET", f"/articles/{article_id}/")


@mcp.tool()
async def approve_article(article_id: int) -> dict:
    """Approve and publish an article.

    Args:
        article_id: ID of the article to publish
    """
    return await api_request("POST", f"/articles/{article_id}/approve/")


@mcp.tool()
async def reject_article(article_id: int) -> dict:
    """Reject an article.

    Args:
        article_id: ID of the article to reject
    """
    return await api_request("POST", f"/articles/{article_id}/reject/")


@mcp.tool()
async def pin_article(article_id: int) -> dict:
    """Pin an article to the top of the list (TOP). Duration is configured in pin_duration_hours.

    Args:
        article_id: ID of the article to pin
    """
    return await api_request("POST", f"/articles/{article_id}/pin/")


@mcp.tool()
async def unpin_article(article_id: int) -> dict:
    """Remove pin from an article (remove from TOP).

    Args:
        article_id: ID of the article to unpin
    """
    return await api_request("POST", f"/articles/{article_id}/unpin/")


@mcp.tool()
async def lock_article(article_id: int) -> dict:
    """Lock an article to protect it from rotation cleanup (LOCK).

    Args:
        article_id: ID of the article to lock
    """
    return await api_request("POST", f"/articles/{article_id}/lock/")


@mcp.tool()
async def unlock_article(article_id: int) -> dict:
    """Unlock an article, allowing it to be removed by rotation cleanup.

    Args:
        article_id: ID of the article to unlock
    """
    return await api_request("POST", f"/articles/{article_id}/unlock/")


@mcp.tool()
async def delete_article(article_id: int) -> str:
    """Delete an article.

    Args:
        article_id: ID of the article to delete
    """
    await api_request("DELETE", f"/articles/{article_id}/")
    return f"Article {article_id} deleted"


@mcp.tool()
async def delete_all_articles() -> dict:
    """Delete ALL articles for this project. Use with caution."""
    data = await api_request("GET", "/articles/", params={"page_size": 200})
    results = data.get("results", [])
    deleted = 0
    errors = 0
    for article in results:
        try:
            await api_request("DELETE", f"/articles/{article['id']}/")
            deleted += 1
        except Exception:
            errors += 1
    return {"deleted": deleted, "errors": errors, "total_found": len(results)}


# ===== Fetch & Stats =====

@mcp.tool()
async def trigger_fetch() -> dict:
    """Trigger a manual news fetch. Fetches articles from all active sources based on configured keywords."""
    return await api_request("POST", "/fetch/")


@mcp.tool()
async def get_stats() -> dict:
    """Get usage statistics: article counts, API calls, fetch history."""
    return await api_request("GET", "/stats/")


# --- Run ---
if __name__ == "__main__":
    mcp.run()
