from types import SimpleNamespace
from unittest import mock

from event_engine import fetch
from event_engine.fetch import extract_text_from_html, fetch_page_text


def test_extract_text_from_html_removes_noise_and_collapses_whitespace():
    html = """
    <html>
      <nav>menu</nav>
      <script>var x=1;</script>
      <p>Hello   world</p>
      <footer>footer</footer>
    </html>
    """

    class DummyTag:
        def decompose(self):
            pass

    class DummySoup:
        def __init__(self, html, parser):
            self.html = html

        def __call__(self, tags):
            return [DummyTag() for _ in tags]

        def get_text(self, separator=" ", strip=True):
            return "Hello   world"

    with mock.patch.object(fetch, "BeautifulSoup", new=DummySoup):
        assert extract_text_from_html(html) == "Hello world"


def test_fetch_page_text_returns_none_when_requests_fails():
    dummy_requests = mock.Mock()
    dummy_requests.get.side_effect = Exception("connection failed")

    with mock.patch.object(fetch, "requests", new=dummy_requests):
        with mock.patch.object(fetch, "BeautifulSoup", new=mock.Mock()):
            assert fetch_page_text("https://example.com") is None


def test_fetch_page_text_returns_clean_text():
    dummy_response = SimpleNamespace(text="<p>Line1</p><script>ignore</script><p>Line2</p>")
    dummy_response.raise_for_status = mock.Mock()

    class DummyTag:
        def decompose(self):
            pass

    class DummySoup:
        def __init__(self, html, parser):
            pass

        def __call__(self, tags):
            return [DummyTag() for _ in tags]

        def get_text(self, separator=" ", strip=True):
            return "Line1 Line2"

    dummy_requests = mock.Mock()
    dummy_requests.get.return_value = dummy_response

    with mock.patch.object(fetch, "requests", new=dummy_requests):
        with mock.patch.object(fetch, "BeautifulSoup", new=DummySoup):
            value = fetch_page_text("https://example.com")
            assert value == "Line1 Line2"
            dummy_requests.get.assert_called_once()
