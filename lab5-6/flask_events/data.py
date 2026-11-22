"""Демонстраційні дані (замість бази даних).

Реєстрації зберігаються в пам'яті й зникають після перезапуску сервера.
"""

from datetime import date

EVENTS: list[dict] = [
    {
        "slug": "python-meetup",
        "title": "Python Meetup Київ",
        "date": date(2026, 12, 5),
        "city": "Київ",
        "category": "Мітап",
        "price": 0,
        "seats_left": 24,
        "description": "Вечір коротких доповідей про нові можливості Python, типізацію "
                       "та інструменти розробника. Після доповідей — нетворкінг і піца.",
    },
    {
        "slug": "django-workshop",
        "title": "Воркшоп: перший сайт на Django",
        "date": date(2026, 12, 12),
        "city": "Львів",
        "category": "Воркшоп",
        "price": 450,
        "seats_left": 8,
        "description": "Практичне заняття: від startproject до розгортання. Створимо "
                       "сайт із шаблонами, формами та адмін-панеллю. Потрібен ноутбук.",
    },
    {
        "slug": "flask-api",
        "title": "Flask для REST API",
        "date": date(2027, 1, 16),
        "city": "Онлайн",
        "category": "Вебінар",
        "price": 300,
        "seats_left": 0,
        "description": "Як побудувати компактний REST API на Flask, організувати "
                       "Blueprint-и, валідацію запитів і документацію OpenAPI.",
    },
    {
        "slug": "data-science-day",
        "title": "Data Science Day",
        "date": date(2027, 2, 6),
        "city": "Харків",
        "category": "Конференція",
        "price": 600,
        "seats_left": 40,
        "description": "Цілий день про аналіз даних: pandas, візуалізація, машинне "
                       "навчання в продакшні та історії успіху українських команд.",
    },
    {
        "slug": "pytest-talk",
        "title": "Тестування з pytest",
        "date": date(2027, 3, 1),
        "city": "Одеса",
        "category": "Мітап",
        "price": 200,
        "seats_left": 15,
        "description": "Фікстури, параметризація, моки та покриття коду. Розберемо "
                       "типові помилки при тестуванні вебзастосунків.",
    },
]

REGISTRATIONS: list[dict] = []


def get_event(slug: str) -> dict | None:
    """Повертає подію за slug або None."""
    return next((e for e in EVENTS if e["slug"] == slug), None)


def event_choices() -> list[tuple[str, str]]:
    """Варіанти для поля вибору події (з порожнім пунктом-підказкою)."""
    return [("", "— оберіть подію —")] + [
        (e["slug"], f"{e['title']} ({e['city']})") for e in EVENTS
    ]
