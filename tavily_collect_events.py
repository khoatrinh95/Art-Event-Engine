import os
from dotenv import load_dotenv
from tavily import TavilyClient

from event_engine.app import collect_event_candidates
from event_engine.config import LOG_FILE, VERBOSE_LOGGING
from event_engine.logger import LoggerEventEngine

def run_tavily_engine():
    load_dotenv()
    tavily_key = os.getenv("TAVILY_API_KEY")

    if not tavily_key:
        print("❌  TAVILY_API_KEY not set. Run: export TAVILY_API_KEY='tvly-...'")
        return

    tavily_client = TavilyClient(api_key=tavily_key)

    LoggerEventEngine.__new__(log_file=LOG_FILE, verbose=VERBOSE_LOGGING)
    logger = LoggerEventEngine.get_logger()

    candidates = collect_event_candidates(tavily_client)
    for i, candidate in enumerate(candidates, 1):
        url = candidate.get("url", "")
        title = candidate.get("title") or url

        logger.info("[%s/%s] %s", i, len(candidates), title[:65])
        logger.info("           %s", url)

if __name__ == "__main__":
    run_tavily_engine()