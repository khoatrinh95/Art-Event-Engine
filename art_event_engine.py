from event_engine.app import analyze_candidates, collect_event_candidates
from event_engine.config import LOCATION, LOG_FILE, VERBOSE_LOGGING
from event_engine.write import write_to_file
from event_engine.logger import LoggerEventEngine
from event_engine.clients import get_clients


def run_engine():
    tavily_client, claude_client = get_clients()

    logger = LoggerEventEngine(log_file=LOG_FILE, verbose=VERBOSE_LOGGING).get_logger()
    logger.start(LOCATION)

    candidates = collect_event_candidates(tavily_client)

    events_found = analyze_candidates(candidates, claude_client)
    
    write_to_file(events_found)



if __name__ == "__main__":
    run_engine()
