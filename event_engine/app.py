from typing import Optional

from .extract import extract_event_data
from .fetch import fetch_page_text
from .filters import has_application_signal
from .search import find_event_urls


def collect_event_candidates(tavily):
    return find_event_urls(tavily)


def analyze_candidate(candidate: dict, claude) -> Optional[dict]:
    source_type = "social_snippet" if candidate.get("is_social") else "webpage"
    page_text = candidate.get("snippet") if source_type == "social_snippet" else fetch_page_text(candidate.get("url", ""))

    if not page_text:
        return None
    if not has_application_signal(page_text):
        return None

    event = extract_event_data(claude, page_text, source_type)
    if event is None:
        return None

    event["source_type"] = source_type
    return event
