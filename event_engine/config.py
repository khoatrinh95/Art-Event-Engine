from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

LOCATION = "Montreal"
CURRENT_YEAR = datetime.now().year

LOG_FILE = ROOT_DIR / "event_engine.log"
VERBOSE_LOGGING = True

SIGNAL_WORDS = [
    "apply", "application", "call for artists", "call for vendors",
    "deadline", "vendor", "juried", "submit", "registration", "booth"
]

MAX_PAGE_CHARS = 12000
MIN_CONFIDENCE = 0.55
FETCH_DELAY = 1.5
VITALY_MAX_RESULT = 5

BLOCKED_DOMAINS = [
    "facebook.com", "fb.com",
    "instagram.com",
    "twitter.com", "x.com",
    "tiktok.com",
    "linkedin.com",
]

SEARCH_QUERIES = [
    f'"call for artists" Montreal {CURRENT_YEAR}',
    f'"call for vendors" "art market" Montreal {CURRENT_YEAR}',
    f'"craft fair" Montreal "apply" {CURRENT_YEAR}',
    f'"pop-up" artists vendors Montreal "apply" {CURRENT_YEAR}',
    f'"art fair" Montreal "application" {CURRENT_YEAR}',
    f'"juried show" OR "juried exhibition" Montreal {CURRENT_YEAR}',
    f'site:eventbrite.com "call for artists" Montreal',
    f'site:instagram.com "call for artists" Montreal {CURRENT_YEAR}',
    f'site:instagram.com "call for vendors" Montreal {CURRENT_YEAR}',
    f'site:facebook.com "call for artists" Montreal {CURRENT_YEAR}',
    f'site:facebook.com "call for vendors" Montreal {CURRENT_YEAR}',
]
