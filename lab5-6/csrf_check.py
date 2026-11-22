"""Емпірична перевірка CSRF-захисту обох проєктів (завдання 6).

Спершу запустіть сервери в окремих терміналах:
    cd django_events && python manage.py runserver     # http://127.0.0.1:8000
    cd flask_events  && python app.py                  # http://127.0.0.1:5000
Потім:
    python csrf_check.py            # обидва
    python csrf_check.py django     # лише Django
    python csrf_check.py flask      # лише Flask

Для кожного сервера виконуються три POST-запити:
  1) без токена й без cookie        -> очікується відмова (Django 403, Flask 400)
  2) з вигаданим токеном            -> очікується відмова
  3) з дійсним токеном зі сторінки  -> очікується 302 (успішна реєстрація)
Скрипт використовує лише стандартну бібліотеку (urllib).
"""

import http.cookiejar
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

TARGETS = {
    "django": {"url": "http://127.0.0.1:8000/register/", "token_field": "csrfmiddlewaretoken"},
    "flask": {"url": "http://127.0.0.1:5000/register", "token_field": "csrf_token"},
}

VALID_DATA = {
    "full_name": "Тарас Перевірка",
    "email": "taras@example.com",
    "event": "python-meetup",
    "message": "Перевіряю роботу CSRF-захисту у навчальному проєкті",
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Не переходити за redirect — щоб побачити саме код 302."""

    def redirect_request(self, *args, **kwargs):
        return None


def post(opener, url: str, data: dict) -> tuple[int, str]:
    body = urllib.parse.urlencode(data).encode()
    request = urllib.request.Request(url, data=body, method="POST")
    try:
        with opener.open(request, timeout=5) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as err:  # 3xx/4xx/5xx
        return err.code, err.read().decode("utf-8", "replace")


def extract_token(page: str, field: str) -> str | None:
    for tag in re.findall(r"<input[^>]+>", page):
        if f'name="{field}"' in tag:
            match = re.search(r'value="([^"]*)"', tag)
            return match.group(1) if match else None
    return None


def short(body: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", body, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()[:110]


def check(name: str, url: str, token_field: str) -> None:
    print(f"\n=== {name.upper()}: {url} ===")
    plain = urllib.request.build_opener(NoRedirect)

    status, body = post(plain, url, VALID_DATA)
    print(f"1) Без токена:            HTTP {status}  | {short(body)}")

    status, body = post(plain, url, {**VALID_DATA, token_field: "fake-token-123"})
    print(f"2) З вигаданим токеном:   HTTP {status}  | {short(body)}")

    jar = http.cookiejar.CookieJar()
    session = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar), NoRedirect)
    with session.open(url, timeout=5) as response:
        page = response.read().decode("utf-8")
    token = extract_token(page, token_field)
    status, body = post(session, url, {**VALID_DATA, token_field: token or ""})
    verdict = "успіх (redirect)" if status == 302 else "неочікувано"
    print(f"3) З дійсним токеном:     HTTP {status}  | {verdict}; токен {token[:12] if token else '—'}…")


def main() -> None:
    selected = sys.argv[1:] or list(TARGETS)
    for name in selected:
        cfg = TARGETS[name]
        try:
            check(name, cfg["url"], cfg["token_field"])
        except urllib.error.URLError as err:
            print(f"\n=== {name.upper()} === сервер недоступний ({err.reason}). Чи запущено його?")


if __name__ == "__main__":
    main()
