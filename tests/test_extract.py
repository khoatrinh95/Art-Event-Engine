from types import SimpleNamespace

from event_engine.extract import build_extraction_prompt, extract_event_data


def test_build_extraction_prompt_includes_social_note():
    prompt = build_extraction_prompt("hello world", today="March 28, 2026", source_type="social_snippet")
    assert "short snippet from a social media post" in prompt
    assert "Today's date is March 28, 2026." in prompt


def test_build_extraction_prompt_includes_webpage_note():
    prompt = build_extraction_prompt("hello world", today="March 28, 2026", source_type="webpage")
    assert "full webpage" in prompt


def test_extract_event_data_parses_json_response():
    class DummyResponse:
        def __init__(self, content):
            self.content = [SimpleNamespace(text=content)]

    claude = SimpleNamespace(messages=SimpleNamespace(create=lambda **kwargs: DummyResponse('{"is_event": true, "event_name": "Test Event"}')))
    result = extract_event_data(claude, "some text", "webpage")
    assert result == {"is_event": True, "event_name": "Test Event"}


def test_extract_event_data_handles_invalid_json():
    class DummyResponse:
        def __init__(self, content):
            self.content = [SimpleNamespace(text=content)]

    claude = SimpleNamespace(messages=SimpleNamespace(create=lambda **kwargs: DummyResponse('not json')))
    assert extract_event_data(claude, "some text", "webpage") is None
