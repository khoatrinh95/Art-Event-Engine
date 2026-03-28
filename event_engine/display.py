def _print_field(label: str, value, indent: int = 2) -> None:
    if value and value != "null":
        pad = " " * indent
        print(f"{pad}  {label:<26} {value}")


def print_event(event: dict, source_url: str, index: int) -> None:
    sep = "─" * 60
    print(f"\n  {sep}")
    print(f"  EVENT #{index}")
    print(f"  {sep}")

    _print_field("Name:", event.get("event_name"))
    _print_field("Type:", event.get("event_type"))
    _print_field("Date:", event.get("event_date"))
    _print_field("Application Deadline:", event.get("application_deadline"))
    _print_field("Location:", event.get("location"))
    _print_field("Theme:", event.get("theme"))
    _print_field("Organizer:", event.get("organizer"))
    _print_field("Size:", event.get("estimated_size"))
    _print_field("Years Running:", event.get("years_running"))
    _print_field("Booth Fee:", event.get("booth_fee"))
    _print_field("How to Apply:", event.get("how_to_apply"))
    _print_field("Source:", event.get("source_type", "webpage").replace("_", " ").title())
    _print_field("Source URL:", source_url)

    sm = event.get("social_media", {}) or {}
    _print_field("Instagram:", sm.get("instagram"))
    _print_field("Facebook:", sm.get("facebook"))
    _print_field("Website:", sm.get("website"))
