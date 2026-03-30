import json
from datetime import datetime

from event_engine.config import LOCATION


def write_to_file(events: list[dict]) -> None:
    if events:
        output_file = f"events_{LOCATION.lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=2, ensure_ascii=False)
        print(f"📄 Full results saved to: {output_file}")