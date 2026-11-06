# mailer.py
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from dotenv import load_dotenv

from parser import Event
import config

load_dotenv()

TEMPLATE = """\
<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;
             background:#f4f5f7;margin:0;padding:24px;color:#1a1a1a">
  <div style="max-width:640px;margin:0 auto">
    <h1 style="font-size:20px;margin:0 0 4px">Новые события Сбера</h1>
    <p style="color:#666;margin:0 0 20px;font-size:13px">
      Найдено {count} новых релевантных событий · {date}
    </p>
    {cards}
    <p style="color:#999;font-size:11px;margin-top:32px;
              border-top:1px solid #e5e5e5;padding-top:12px">
      Автоматическая рассылка парсера developers.sber.ru/kak-v-sbere
    </p>
  </div>
</body></html>
"""

CARD = """\
<div style="background:#fff;border-radius:10px;padding:16px 18px;
            margin-bottom:12px;border:1px solid #e8e8e8">
  <div style="font-size:11px;text-transform:uppercase;letter-spacing:.5px;
              color:#{type_color};font-weight:600;margin-bottom:4px">
    {type}{online_badge}
  </div>
  <div style="font-size:16px;font-weight:600;margin-bottom:6px">{title}</div>
  <div style="font-size:13px;color:#555;margin-bottom:10px">{desc}</div>
  <div style="font-size:13px;color:#333;margin-bottom:4px">
    📅 {date}{time}
  </div>
  <div style="font-size:13px;color:#333;margin-bottom:10px">
    📍 {place}
  </div>
  <div style="font-size:12px;color:#888;margin-bottom:12px">
    🏷 {tags}
  </div>
  {button}
</div>
"""


def _fmt_date_range(ev: Event) -> str:
    if ev.start_date == ev.end_date:
        return ev.start_date.strftime("%d.%m.%Y")
    return f"{ev.start_date.strftime('%d.%m')} – {ev.end_date.strftime('%d.%m.%Y')}"


def _render_card(ev: Event) -> str:
    et = ev.event_type.lower()
    if "хакатон" in et or "hackathon" in et:
        type_color = "e04a1a"
        type_label = "Хакатон"
    elif ev.event_type:
        type_color = "1a6ee0"
        type_label = ev.event_type
    else:
        type_color = "666"
        type_label = "Событие"

    online_badge = " · 🌐 онлайн" if ev.is_online else ""
    time_str = f", {ev.start_time}" if ev.start_time else ""
    place = "Онлайн" if ev.is_online else (ev.place or "—")
    tags = ", ".join(ev.tags) if ev.tags else "—"

    if ev.url:
        button = (
            f'<a href="{ev.url}" style="display:inline-block;background:#1a1a1a;'
            f'color:#fff;text-decoration:none;padding:8px 16px;border-radius:6px;'
            f'font-size:13px;font-weight:500">Участвовать →</a>'
        )
    else:
        button = (
            '<span style="font-size:12px;color:#999">'
            'Ссылка на регистрацию пока не опубликована</span>'
        )

    return CARD.format(
        type_color=type_color, type=type_label, online_badge=online_badge,
        title=ev.title, desc=ev.description or "—",
        date=_fmt_date_range(ev), time=time_str, place=place,
        tags=tags, button=button,
    )


def render_html(events: list[Event]) -> str:
    from datetime import date
    cards = "\n".join(_render_card(ev) for ev in events)
    return TEMPLATE.format(
        count=len(events),
        date=date.today().strftime("%d.%m.%Y"),
        cards=cards,
    )


def send_email(events: list[Event]) -> None:
    if not events:
        return
    host = os.environ[config.SMTP_HOST_ENV]
    port = int(os.environ[config.SMTP_PORT_ENV])
    user = os.environ[config.SMTP_USER_ENV]
    pwd = os.environ[config.SMTP_PASS_ENV]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Новые события Сбера ({len(events)})"
    msg["From"] = user
    msg["To"] = config.EMAIL_TO
    msg.attach(MIMEText(render_html(events), "html", "utf-8"))

    with smtplib.SMTP_SSL(host, port) as s:
        s.login(user, pwd)
        s.send_message(msg)