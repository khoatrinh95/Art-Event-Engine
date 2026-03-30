from typing import Any

from .config import BLOCKED_DOMAINS, VITALY_MAX_RESULT, SEARCH_QUERIES
from .logger import LoggerEventEngine

logger = LoggerEventEngine.get_logger()


def is_blocked_domain(url: str) -> bool:
    """Return True if the URL is from a blocked social media domain."""
    return any(domain in url for domain in BLOCKED_DOMAINS)


def find_event_urls(tavily: Any) -> list[dict]:
    """
    Run all search queries and collect unique URLs + snippets.
    Returns a list of dicts: { url, title, snippet, is_social }
    """
    seen_urls = set()
    results = []

    for query in SEARCH_QUERIES:
        logger.info("\n  🔍 Query: %s", query)
        try:
            response = tavily.search(
                query=query,
                max_results=VITALY_MAX_RESULT,
                search_depth="basic"
            )
            for r in response.get("results", []):
                url = r.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    social = is_blocked_domain(url)
                    results.append({
                        "url": url,
                        "title": r.get("title", ""),
                        "snippet": r.get("content", ""),
                        "is_social": social,
                    })
                    tag = "📱" if social else "  "
                    logger.info("     %s + %s: %s", tag, "title", r.get("title", url)[:67])
                    logger.info("     %s + %s: %s", tag, "url", url)
                    logger.info("     %s + %s: %s", tag, "snippet", r.get("content", "")[:500])
        except Exception as exc:
            logger.error("     ✗ Search failed: %s", exc)
            logger.debug("Search exception details for query %s", query, exc_info=True)

    logger.info("\n  ✅ Found %s unique URLs to check\n", len(results))
    return results
