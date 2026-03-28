import re
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ModuleNotFoundError:  # pragma: no cover
    requests = None
    BeautifulSoup = None

from .config import MAX_PAGE_CHARS

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
        print("     ✗ Fetch failed: requests and bs4 are required")
        return None

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()
        return extract_text_from_html(response.text)[:MAX_PAGE_CHARS]

    except Exception as exc:
        print(f"     ✗ Fetch failed: {exc}")
        return None
