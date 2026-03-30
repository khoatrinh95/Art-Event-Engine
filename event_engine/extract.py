import json
from datetime import datetime
from typing import Any, Optional

from .config import LOCATION
from .logger import LoggerEventEngine

logger = LoggerEventEngine.get_logger()


def build_extraction_prompt(page_text: str, today: Optional[str] = None, source_type: str = "webpage") -> str:
    """Build the Claude prompt for event extraction."""
    if today is None:
        today = datetime.now().strftime("%B %d, %Y")

    source_note = (
        "NOTE: This content is a short snippet from a social media post. "
        "It may not contain all details. Extract what you can and set "
        "confidence_score lower if key fields like deadline are missing."
        if source_type == "social_snippet"
        else "NOTE: This content is from a full webpage."
    )

    return f"""You are an assistant helping artists find events to apply to.

Analyze the text below and extract structured event information.

{source_note}

IMPORTANT FILTERING RULES:
- Today's date is {today}.
- If the event_date has already passed, set is_calling_for_artists to false.
- If the application_deadline has already passed, set is_calling_for_artists to false.
- Only return true for is_calling_for_artists if the event is still in the future
  AND applications are still open (or opening date is unknown).

Return ONLY a valid JSON object — no explanation, no markdown, no backticks.

JSON fields to extract:
{{
  "is_event": true,
  "is_calling_for_artists": true,
  "event_name": "...",
  "event_type": "art fair | craft fair | pop-up | gallery show | other",
  "event_date": "...",
  "application_deadline": "...",
  "location": "...",
  "description": "...",
  "theme": "...",
  "how_to_apply": "...",
  "estimated_size": "small | medium | large | unknown",
  "years_running": "...",
  "organizer": "...",
  "social_media": {{
    "instagram": "...",
    "facebook": "...",
    "website": "..."
  }},
  "booth_fee": "...",
  "confidence_score": 0.0
}}

Use null for any field not found.
Set confidence_score (0.0 to 1.0) based on how clearly the text confirms this is a
real, upcoming event actively seeking artists/vendors.

TEXT:
{page_text}"""


def extract_event_data(claude: Any, page_text: str, source_type: str = "webpage") -> Optional[dict]:
    """Send page text to Claude and parse the JSON result."""
    today = datetime.now().strftime("%B %d, %Y")
    try:
        message = claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": build_extraction_prompt(page_text, today, source_type)
            }]
        )

        raw = message.content[0].text.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        result = json.loads(raw)
        logger.debug("Extracted JSON result from Claude: %s", result)
        return result

    except json.JSONDecodeError as exc:
        logger.warning("     ✗ JSON parse error: %s", exc)
        logger.debug("Raw Claude response for failed parse: %s", raw)
        return None
    except Exception as exc:
        logger.error("     ✗ Claude API error: %s", exc)
        logger.debug("Claude API exception details", exc_info=True)
        return None
