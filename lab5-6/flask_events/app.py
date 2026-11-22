"""Точка входу Flask-проєкту «ПодіїUA».

Запуск:  python app.py      (або  flask --app app run)
"""

from collections import Counter
from datetime import date

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFError, CSRFProtect

from config import Config
from data import EVENTS, REGISTRATIONS, get_event
from forms import RegistrationForm

MONTHS_GENITIVE = [
    "січня", "лютого", "березня", "квітня", "травня", "червня",
    "липня", "серпня", "вересня", "жовтня", "листопада", "грудня",
]
WEEKDAYS = ["понеділок", "вівторок", "середа", "четвер", "п'ятниця", "субота", "неділя"]

csrf = CSRFProtect()


def ua_date(value: date, fmt: str = "long") -> str:
    """Jinja-фільтр: дата українською ('5 грудня 2026', '05.12.2026' або день тижня)."""
    if fmt == "short":
        return value.strftime("%d.%m.%Y")
    if fmt == "weekday":
        return WEEKDAYS[value.weekday()]
    return f"{value.day} {MONTHS_GENITIVE[value.month - 1]} {value.year}"


def create_app(config_class: type = Config) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(config_class.TEMPLATE_FOLDER),
        static_folder=str(config_class.STATIC_FOLDER),
    )
    app.config.from_object(config_class)
    csrf.init_app(app)  # CSRF для ВСІХ POST-запитів, навіть поза FlaskForm

    app.add_template_filter(ua_date, "ua_date")

    @app.context_processor
    def inject_globals() -> dict:
        """Змінні, доступні в усіх шаблонах (для підвалу в base.html)."""
        return {"current_year": date.today().year}

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            site_slogan="Афіша IT-подій для студентів і розробників",
            events_total=len(EVENTS),
            featured=EVENTS[:3],
            categories=dict(Counter(e["category"] for e in EVENTS)),
            registrations=REGISTRATIONS[-5:][::-1],
            events=EVENTS,
        )

    @app.route("/events")
    def events():
        return render_template(
            "events.html",
            heading="Усі події",
            events=EVENTS,
            xss_sample="<script>alert('XSS')</script>",
        )

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegistrationForm()
        if request.method == "GET" and request.args.get("event"):
            form.event.data = request.args["event"]

        if form.validate_on_submit():          # POST + CSRF + усі валідатори
            event = get_event(form.event.data)
            event["seats_left"] -= 1
            REGISTRATIONS.append({
                "name": form.full_name.data,
                "email": form.email.data,
                "event": event["title"],
            })
            flash(
                f"{form.full_name.data}, вас зареєстровано на «{event['title']}». "
                f"Підтвердження надіслано на {form.email.data}.",
                "success",
            )
            return redirect(url_for("index"))  # Post/Redirect/Get

        if form.is_submitted():
            flash("Форму не надіслано — виправте помилки нижче.", "error")
        return render_template("register.html", form=form)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error: CSRFError):
        return render_template("csrf_error.html", reason=error.description), 400

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
