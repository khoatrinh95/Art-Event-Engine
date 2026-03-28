import json
import os
import time
from datetime import datetime

from dotenv import load_dotenv
from tavily import TavilyClient
import anthropic

from event_engine.app import analyze_candidate, collect_event_candidates
from event_engine.config import FETCH_DELAY, LOCATION, MIN_CONFIDENCE
from event_engine.display import print_event


def run_engine():
    load_dotenv()
    tavily_key = os.getenv("TAVILY_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if not tavily_key:
        print("❌  TAVILY_API_KEY not set. Run: export TAVILY_API_KEY='tvly-...'")
        return
    if not anthropic_key:
        print("❌  ANTHROPIC_API_KEY not set. Run: export ANTHROPIC_API_KEY='sk-ant-...'")
        return

    tavily_client = TavilyClient(api_key=tavily_key)
    claude_client = anthropic.Anthropic(api_key=anthropic_key)

    print(f"Art Event Engine — {LOCATION}")
    print(f"    {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    candidates = collect_event_candidates(tavily_client)
    events_found = []
    skipped = 0
    skipped_not_event = 0
    skipped_low_confidence = 0

    print(f"{'='*60}")
    print(f"  STAGE 2: Fetching & extracting event data")
    print(f"{'='*60}")

    for i, candidate in enumerate(candidates, 1):
        url = candidate.get("url", "")
        title = candidate.get("title") or url
        is_social = candidate.get("is_social", False)
        min_confidence = MIN_CONFIDENCE - 0.15 if is_social else MIN_CONFIDENCE

        print(f"[{i}/{len(candidates)}] {title[:65]}")
        print(f"           {url[:65]}")

        event_data = analyze_candidate(candidate, claude_client)
        if not event_data:
            skipped += 1
            time.sleep(FETCH_DELAY)
            continue

        if not event_data.get("is_event") or not event_data.get("is_calling_for_artists"):
            print(f"     ⏭  Not an active call for artists")
            skipped_not_event += 1
            time.sleep(FETCH_DELAY)
            continue

        confidence = event_data.get("confidence_score", 0)
        if confidence < min_confidence:
            print(f"     ⏭  Low confidence ({confidence:.0%}) — skipping")
            skipped_low_confidence += 1
            time.sleep(FETCH_DELAY)
            continue

        print(f"     ✅  Event found! ({confidence:.0%} confidence)")
        event_data["source_url"] = url
        events_found.append(event_data)
        time.sleep(FETCH_DELAY)

    print(f"{'='*60}")
    print(f"  RESULTS — {len(events_found)} events found in {LOCATION}")
    print(f"{'='*60}")

    if not events_found:
        print("No events found. Try:")
        print("  - Broadening the search queries")
        print("  - Lowering MIN_CONFIDENCE threshold")
        print("  - Checking your API keys are valid")
    else:
        for i, event in enumerate(events_found, 1):
            print_event(event, event.get("source_url", ""), i)

    print(f"{'='*60}")
    print(f"  RUN SUMMARY")
    print(f"{'='*60}")
    print(f"  URLs found by search:      {len(candidates)}")
    print(f"  Skipped candidates:        {skipped}")
    print(f"  Skipped (not an event):    {skipped_not_event}")
    print(f"  Skipped (low confidence):  {skipped_low_confidence}")
    print(f"  Events saved:              {len(events_found)}")

    if events_found:
        output_file = f"events_{LOCATION.lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(events_found, f, indent=2, ensure_ascii=False)
        print(f"📄 Full results saved to: {output_file}")

    print("Done.")


if __name__ == "__main__":
    run_engine()
