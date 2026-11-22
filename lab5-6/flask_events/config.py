"""Конфігурація Flask-проєкту «ПодіїUA».

SECRET_KEY читається зі змінної оточення FLASK_SECRET_KEY і в код не потрапляє.
"""

import os
import secrets
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _secret_key() -> str:
    key = os.environ.get("FLASK_SECRET_KEY", "")
    if not key:
        # Тимчасовий ключ для локальної розробки (змінюється при перезапуску).
        print("[config] FLASK_SECRET_KEY не задано — використано тимчасовий ключ", file=sys.stderr)
        key = secrets.token_hex(32)
    return key


class Config:
    SECRET_KEY = _secret_key()          # підписує сесію, flash і CSRF-токени
    DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"
    TEMPLATE_FOLDER = BASE_DIR / "templates"
    STATIC_FOLDER = BASE_DIR / "static"
    WTF_CSRF_ENABLED = True             # CSRF для всіх FlaskForm
    WTF_CSRF_TIME_LIMIT = 3600          # токен дійсний 1 годину
