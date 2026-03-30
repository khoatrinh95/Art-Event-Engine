from .config import SIGNAL_WORDS


def has_application_signal(text: str) -> bool:
    """Return True when the text contains a likely application-related signal."""
    lower_text = text.lower()
    return any(word in lower_text for word in SIGNAL_WORDS)


if __name__ == "__main__":
    import sys

    text = sys.argv[1]
    result = has_application_signal(text)
    sep = "─" * 60
    print(f"\n  {sep}")
    print(result)