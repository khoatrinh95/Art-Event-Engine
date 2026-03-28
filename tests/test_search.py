from event_engine.search import find_event_urls, is_blocked_domain


class DummyTavily:
    def __init__(self, results):
        self.results = results

    def search(self, query, max_results, search_depth):
        return {"results": self.results}


def test_is_blocked_domain_detects_social_media():
    assert is_blocked_domain("https://www.instagram.com/call-for-artists")
    assert is_blocked_domain("https://x.com/art-event")
    assert not is_blocked_domain("https://montrealartfair.com/apply")


def test_find_event_urls_deduplicates_and_marks_social():
    tavily = DummyTavily([
        {"url": "https://example.com/1", "title": "Event 1", "content": "info"},
        {"url": "https://example.com/1", "title": "Event 1 dup", "content": "info"},
        {"url": "https://instagram.com/post", "title": "Social Post", "content": "snippet"},
    ])

    results = find_event_urls(tavily)

    assert len(results) == 2
    assert results[0]["url"] == "https://example.com/1"
    assert results[1]["is_social"]
    assert results[1]["snippet"] == "snippet"
