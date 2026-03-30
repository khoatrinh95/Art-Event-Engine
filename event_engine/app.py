from typing import Optional

import time

from event_engine.config import LOCATION, FETCH_DELAY, MIN_CONFIDENCE
from event_engine.display import print_results, print_summary

from .extract import extract_event_data
from .fetch import fetch_page_text
from .filters import has_application_signal
from .logger import LoggerEventEngine
from .search import find_event_urls

logger = LoggerEventEngine.get_logger()


def collect_event_candidates(tavily) -> list[dict]:
    logger.header(f"STAGE 1: Searching for events in {LOCATION}")
    candidates = find_event_urls(tavily)
    logger.info("Collected %s candidates from search", len(candidates))
    return candidates


def analyze_candidates(candidates: list[dict], claude_client) -> list[dict]:
    logger.header("STAGE 2: Fetching & extracting event data")
    events_found = []
    skipped = 0
    skipped_not_event = 0
    skipped_low_confidence = 0

    for i, candidate in enumerate(candidates, 1):
        url = candidate.get("url", "")
        title = candidate.get("title") or url
        is_social = candidate.get("is_social", False)
        min_confidence = MIN_CONFIDENCE - 0.15 if is_social else MIN_CONFIDENCE

        logger.info("[%s/%s] %s", i, len(candidates), title[:65])
        logger.info("           %s", url)

        event_data = analyze_candidate(candidate, claude_client)
        if not event_data:
            skipped += 1
            time.sleep(FETCH_DELAY)
            continue

        if not event_data.get("is_event") or not event_data.get("is_calling_for_artists"):
            logger.info("     ⏭  Not an active call for artists for %s", url)
            skipped_not_event += 1
            time.sleep(FETCH_DELAY)
            continue

        confidence = event_data.get("confidence_score", 0)
        if confidence < min_confidence:
            logger.info("     ⏭  Low confidence (%s) for %s — skipping", confidence, url)
            skipped_low_confidence += 1
            time.sleep(FETCH_DELAY)
            continue

        logger.info("     ✅  Event found! (%s confidence) from %s", f"{confidence:.0%}", url)
        event_data["source_url"] = url
        events_found.append(event_data)
        time.sleep(FETCH_DELAY)
    
    logger.header(f"RESULTS: {len(events_found)} events found in {LOCATION}")
    logger.info("Run summary: URLs=%s, skipped=%s, skipped_not_event=%s, skipped_low_confidence=%s, events_saved=%s",
                len(candidates), skipped, skipped_not_event, skipped_low_confidence, len(events_found))
    
    print_results(events_found)
    print_summary(
        Total_URLs_found=len(candidates),
        Skipped_Candidates=skipped,
        Skipped_Not_Event=skipped_not_event,
        Skipped_Low_Confidence=skipped_low_confidence,
        Events_Found=len(events_found),
    )
    return events_found

def analyze_candidate(candidate: dict, claude) -> Optional[dict]:
    url = candidate.get("url", "<unknown>")
    source_type = "social_snippet" if candidate.get("is_social") else "webpage"
    logger.info("Analyzing candidate: %s (%s)", url, source_type)

    page_text = candidate.get("snippet") if source_type == "social_snippet" else fetch_page_text(url)
    if not page_text:
        logger.info("Candidate skipped: no page text extracted for %s", url)
        return None

    has_signal = has_application_signal(page_text)
    logger.debug("has_application_signal=%s for %s", has_signal, url)
    if not has_signal:
        logger.info("Candidate skipped: no application signal in %s", url)
        logger.debug("Page excerpt: %s", page_text[:500])
        return None

    event = extract_event_data(claude, page_text, source_type)
    if event is None:
        logger.info("Candidate skipped: extraction failed for %s", url)
        return None

    logger.info(
        "Extraction result for %s: is_event=%s, is_calling_for_artists=%s, confidence=%s",
        url,
        event.get("is_event"),
        event.get("is_calling_for_artists"),
        event.get("confidence_score"),
    )
    logger.debug("Extracted event object for %s: %s", url, event)
    event["source_type"] = source_type
    return event
