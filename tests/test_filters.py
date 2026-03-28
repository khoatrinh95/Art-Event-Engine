from event_engine.filters import has_application_signal


def test_has_application_signal_detects_keywords():
    assert has_application_signal("Submit your application now")
    assert has_application_signal("Call for artists")
    assert not has_application_signal("This is a news article about art")
