# config.py
from dataclasses import dataclass, field

# --- Настройки пользователя ---
USER_CITY = "Ставрополь"          # ваш город
EMAIL_TO = "pixynimble@gmail.com" # куда присылать

# --- SMTP (заполните в .env, здесь только имена переменных) ---
SMTP_HOST_ENV = "SMTP_HOST"
SMTP_PORT_ENV = "SMTP_PORT"
SMTP_USER_ENV = "SMTP_USER"
SMTP_PASS_ENV = "SMTP_PASS"

# --- Фильтры релевантности ---
# Событие попадает в письмо, если score >= THRESHOLD
THRESHOLD = 3.0

# Типы событий (первый бейдж с EventFlagBadge=true)
HACKATHON_TYPES = {"хакатон", "hackathon"}
MEETUP_TYPES = {"meetup", "митап", "конференция", "conference"}

# Профильные темы (проверяем по тегам + названию + описанию, регистр не важен)
TOPIC_KEYWORDS = [
    "ai", "ml", "machine learning", "data science", "datascience", "ds",
    "recsys", "recommendation", "рекомендат", "gigachat", "genai",
    "агент", "agent", "аналитик", "analytics", "нейросет", "neural",
    "llm", "вайбкод", "vibe", "research", "наука",
]

# Стоп-слова: события с этими маркерами штрафуются
NEGATIVE_KEYWORDS = [
    "опыт от", "опыт более", "для экспертов", "закрытая встреча",
    "senior", "lead", "архитектор", "для специалистов с опытом",
]

# Веса
W_HACKATHON = 5.0
W_MEETUP = 1.0
W_TOPIC_MATCH = 3.0
W_ONLINE = 3.0
W_OFFLINE_MY_CITY = 1.0
W_OFFLINE_OTHER_CITY = 0.0
W_NEGATIVE = -4.0
W_NO_URL = -1.0   # если нет ссылки на регистрацию — чуть менее полезно