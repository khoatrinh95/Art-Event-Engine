import io
from contextlib import redirect_stdout

from event_engine.display import print_event


def test_print_event_outputs_expected_fields():
    event = {
        "event_name": "Test Event",
        "event_type": "art fair",
        "event_date": "June 1, 2026",
        "application_deadline": "May 15, 2026",
        "location": "Montreal",
        "theme": "Art & Design",
        "organizer": "Organizers Inc",
        "estimated_size": "medium",
        "years_running": "5",
        "booth_fee": "$50",
        "how_to_apply": "Apply online",
        "source_type": "webpage",
        "social_media": {
            "instagram": "@event",
            "facebook": "facebook.com/event",
            "website": "https://example.com"
        }
    }
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        print_event(event, "https://example.com", 1)

    output = buffer.getvalue()
    assert "EVENT #1" in output
    assert "Test Event" in output
    assert "Instagram:" in output
    assert "facebook.com/event" in output
