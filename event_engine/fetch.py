import re
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ModuleNotFoundError:  # pragma: no cover
    requests = None
    BeautifulSoup = None

from .config import MAX_PAGE_CHARS
from .logger import LoggerEventEngine

logger = LoggerEventEngine.get_logger()

'''
Function to extract text from html, return a clean one-line string with normalized spacing.
     1. Remove all elements that contain navigation, page layout, scripts, styles, or hidden content that is not part of the main readable text.
     2. Extract all remaining visible text from the HTML (Joins text nodes with a single space, strip=True removes leading/trailing whitespace)
     3. Collapse the text into a clean one-line string with normalized spacing.
'''
def extract_text_from_html(html: str) -> str:
    if BeautifulSoup is None:
        raise RuntimeError("BeautifulSoup is required to extract HTML text")

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["nav", "footer", "script", "style", "header", "aside", "iframe", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r"\s+", " ", text)


def fetch_page_text(url: str) -> Optional[str]:
    """Fetch a URL and return clean text content, or None on failure."""
    if requests is None or BeautifulSoup is None:
        logger.error("     ✗ Fetch failed: requests and bs4 are required")
        return None

    logger.debug("Fetching page text: %s", url)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=12)
        clean_text = extract_text_from_html(response.text)[:MAX_PAGE_CHARS]
        logger.debug("Fetched %s chars from %s", len(clean_text), url)
        return clean_text

    except Exception as exc:
        logger.error("     ✗ Fetch failed: %s", exc)
        logger.debug("Fetch exception details for %s", url, exc_info=True)
        return None

if __name__ == "__main__":
    import sys

    url = sys.argv[1]
    result = fetch_page_text(url)
    print(result)