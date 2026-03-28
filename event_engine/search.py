from typing import Any

from .config import BLOCKED_DOMAINS, LOCATION, SEARCH_QUERIES


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

    print(f"\n{'='*60}")
    print(f"  STAGE 1: Searching for events in {LOCATION}")
    print(f"{'='*60}")

    for query in SEARCH_QUERIES:
        print(f"\n  🔍 Query: {query}")
        try:
            response = tavily.search(
                query=query,
                max_results=5,
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
                    print(f"     {tag} + {r.get('title', url)[:67]}")
        except Exception as exc:
            print(f"     ✗ Search failed: {exc}")

    print(f"\n  ✅ Found {len(results)} unique URLs to check\n")
    return results
