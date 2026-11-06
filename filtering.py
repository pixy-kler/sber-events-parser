# filtering.py
from datetime import date
import config
from parser import Event


def _text_blob(ev: Event) -> str:
    parts = [ev.title, ev.description, ev.event_type] + ev.tags
    return " ".join(parts).lower()


def score(ev: Event, today: date) -> float:
    s = 0.0
    blob = _text_blob(ev)
    et = ev.event_type.lower()

    # Тип
    if et in config.HACKATHON_TYPES:
        s += config.W_HACKATHON
    elif et in config.MEETUP_TYPES:
        s += config.W_MEETUP
    else:
        # иногда тип не в первом бейдже — ищем по тегам/названию
        if "хакатон" in blob:
            s += config.W_HACKATHON
        elif "митап" in blob or "meetup" in blob:
            s += config.W_MEETUP

    # Тема
    if any(kw in blob for kw in config.TOPIC_KEYWORDS):
        s += config.W_TOPIC_MATCH

    # Формат
    if ev.is_online:
        s += config.W_ONLINE
    elif ev.city and ev.city.lower() == config.USER_CITY.lower():
        s += config.W_OFFLINE_MY_CITY
    else:
        s += config.W_OFFLINE_OTHER_CITY

    # Негативные маркеры
    if any(kw in blob for kw in config.NEGATIVE_KEYWORDS):
        s += config.W_NEGATIVE

    # Нет ссылки — чуть менее полезно
    if not ev.url:
        s += config.W_NO_URL

    return s


def filter_events(events: list[Event], today: date | None = None) -> list[Event]:
    """Оставляет только будущие и релевантные события, сортирует по дате."""
    today = today or date.today()
    scored = []
    for ev in events:
        if ev.end_date < today:
            continue  # прошедшее
        sc = score(ev, today)
        if sc >= config.THRESHOLD:
            scored.append((sc, ev))
    scored.sort(key=lambda x: (x[1].start_date, -x[0]))
    return [ev for _, ev in scored]