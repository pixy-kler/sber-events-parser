# parser.py
import json
import re
import requests
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from pathlib import Path

URL = "https://developers.sber.ru/kak-v-sbere"
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0 Safari/537.36"),
    "Accept-Language": "ru-RU,ru;q=0.9",
}


@dataclass
class Event:
    slug: str
    title: str
    description: str
    start_date: date
    end_date: date
    start_time: Optional[str]
    place: str
    city: Optional[str]
    is_online: bool
    event_type: str          # "Хакатон" / "Meetup" / ...
    tags: list[str]
    url: Optional[str]

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "start_time": self.start_time,
            "place": self.place,
            "city": self.city,
            "is_online": self.is_online,
            "event_type": self.event_type,
            "tags": self.tags,
            "url": self.url,
        }


def fetch_next_data() -> dict:
    """Скачивает страницу и достаёт __NEXT_DATA__."""
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        resp.text, re.S,
    )
    if not m:
        raise RuntimeError("__NEXT_DATA__ не найден — изменилась вёрстка?")
    return json.loads(m.group(1))


def _collect_event_pages(obj, found: list) -> None:
    if isinstance(obj, dict):
        if obj.get("__typename") == "EventPage":
            found.append(obj)
        for v in obj.values():
            _collect_event_pages(v, found)
    elif isinstance(obj, list):
        for v in obj:
            _collect_event_pages(v, found)


def _parse_date(s: str) -> Optional[date]:
    if not s:
        return None
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _parse_time(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    # "18:30:00.000" -> "18:30"
    return s[:5]


_ONLINE_MARKERS = ("онлайн", "online", "вебинар", "webinar", "трансляц")


def _detect_online(place: str) -> bool:
    if not place:
        return True   # пустое место => считаем онлайн (часто так и есть)
    p = place.lower()
    return any(m in p for m in _ONLINE_MARKERS)


def _extract_city(place: str) -> Optional[str]:
    """Берём первый сегмент до запятой как город (если это офлайн)."""
    if not place or _detect_online(place):
        return None
    first = place.split(",")[0].strip()
    # города — обычно одно-два слова, без цифр
    if first and not re.search(r"\d", first) and len(first) < 40:
        return first
    return None


def _extract_type_and_tags(badges: list[dict]) -> tuple[str, list[str]]:
    event_type = ""
    tags: list[str] = []
    for b in badges or []:
        title = (b.get("BadgeTitle") or "").strip()
        if not title:
            continue
        if b.get("EventFlagBadge") and not event_type:
            event_type = title
        else:
            tags.append(title)
    return event_type, tags


def parse_events(raw: dict) -> list[Event]:
    """Превращает __NEXT_DATA__ в список Event."""
    pages: list[dict] = []
    _collect_event_pages(raw, pages)

    result: list[Event] = []
    for p in pages:
        start = _parse_date(p.get("StartDate"))
        end = _parse_date(p.get("EndDate")) or start
        if not start:
            continue

        place = (p.get("Place") or "").strip()
        is_online = _detect_online(place)
        city = _extract_city(place)

        event_type, tags = _extract_type_and_tags(p.get("EventBadges") or [])

        btn = p.get("CardButton") or {}
        url = btn.get("Url") or p.get("EventUrl")

        title = (p.get("CardTitle") or p.get("Title") or "").strip()
        desc = (p.get("CardDescription") or "").strip()

        result.append(Event(
            slug=p.get("slug") or "",
            title=title,
            description=desc,
            start_date=start,
            end_date=end,
            start_time=_parse_time(p.get("StartTime")),
            place=place,
            city=city,
            is_online=is_online,
            event_type=event_type,
            tags=tags,
            url=url,
        ))
    return result