# storage.py
import json
from pathlib import Path
from parser import Event

SEEN_FILE = Path("seen_events.json")


def load_seen() -> set[str]:
    if not SEEN_FILE.exists():
        return set()
    try:
        return set(json.loads(SEEN_FILE.read_text(encoding="utf-8")))
    except Exception:
        return set()


def save_seen(slugs: set[str]) -> None:
    SEEN_FILE.write_text(
        json.dumps(sorted(slugs), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def pick_new(events: list[Event], seen: set[str]) -> list[Event]:
    """События, которых ещё не было в seen (по slug)."""
    return [ev for ev in events if ev.slug and ev.slug not in seen]


def mark_seen(events: list[Event]) -> set[str]:
    seen = load_seen()
    seen.update(ev.slug for ev in events if ev.slug)
    save_seen(seen)
    return seen