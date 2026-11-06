# main.py
import logging
from datetime import date
from parser import fetch_next_data, parse_events
from filtering import filter_events
from storage import load_seen, pick_new, mark_seen
from mailer import send_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("parser.log", encoding="utf-8"),
              logging.StreamHandler()],
)
log = logging.getLogger(__name__)


def main() -> None:
    log.info("Запуск парсера")
    raw = fetch_next_data()
    events = parse_events(raw)
    log.info("Событий всего: %d", len(events))

    relevant = filter_events(events, today=date.today())
    log.info("Релевантных (score>=порог, будущие): %d", len(relevant))

    seen = load_seen()
    new_events = pick_new(relevant, seen)
    log.info("Новых: %d", len(new_events))

    if not new_events:
        log.info("Нет новых — письмо не отправляем")
        return

    for ev in new_events:
        log.info("  • [%s] %s — %s", ev.event_type or "?",
                 ev.start_date, ev.title)

    send_email(new_events)
    mark_seen(new_events)
    log.info("Письмо отправлено, события помечены как seen")


if __name__ == "__main__":
    main()