"""Форма реєстрації Flask-WTF — еквівалент Django RegistrationForm (завдання 5)."""

import re

from flask_wtf import FlaskForm
from wtforms import EmailField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError

from data import event_choices, get_event

NAME_RE = re.compile(r"^[A-Za-zА-Яа-яІіЇїЄєҐґ'ʼ’\- ]+$")
MIN_MESSAGE_WORDS = 5


class RegistrationForm(FlaskForm):
    full_name = StringField(
        "Ім'я та прізвище",
        validators=[
            DataRequired(message="Вкажіть ім'я та прізвище."),
            Length(min=3, max=60, message="Довжина імені: від %(min)d до %(max)d символів."),
        ],
        render_kw={"placeholder": "Олена Шевченко", "autocomplete": "name"},
    )
    email = EmailField(
        "Електронна пошта",
        validators=[
            DataRequired(message="Вкажіть електронну пошту."),
            Email(message="Введіть коректну адресу, наприклад name@example.com."),
        ],
        render_kw={"placeholder": "name@example.com", "autocomplete": "email"},
    )
    event = SelectField(
        "Подія",
        choices=event_choices(),
        validators=[DataRequired(message="Оберіть подію зі списку.")],
        validate_choice=False,  # наявність події перевіряє validate_event() українською
    )
    message = TextAreaField(
        "Чому ви хочете взяти участь?",
        validators=[
            DataRequired(message="Напишіть кілька слів про свою мотивацію."),
            Length(max=1000, message="Не більше %(max)d символів."),
        ],
        description=f"Щонайменше {MIN_MESSAGE_WORDS} слів, без посилань.",
        render_kw={"rows": 5, "placeholder": "Кілька речень про ваші очікування"},
    )

    def validate_full_name(self, field) -> None:
        """Ім'я: лише літери, пробіл, апостроф, дефіс; щонайменше два слова."""
        value = " ".join((field.data or "").split())
        if not NAME_RE.match(value):
            raise ValidationError("Ім'я може містити лише літери, пробіл, апостроф і дефіс.")
        if len(value.split()) < 2:
            raise ValidationError("Вкажіть і ім'я, і прізвище.")
        field.data = value

    def validate_message(self, field) -> None:
        """Мотивація: щонайменше MIN_MESSAGE_WORDS слів і жодних посилань."""
        value = (field.data or "").strip()
        if re.search(r"https?://|www\.", value, re.IGNORECASE):
            raise ValidationError("Посилання в повідомленні заборонені.")
        words = re.findall(r"\w+", value)
        if len(words) < MIN_MESSAGE_WORDS:
            raise ValidationError(
                f"Напишіть щонайменше {MIN_MESSAGE_WORDS} слів (зараз {len(words)})."
            )
        field.data = value

    def validate_event(self, field) -> None:
        """Бізнес-правило: на подію без вільних місць зареєструватися не можна."""
        event = get_event(field.data)
        if event is None:
            raise ValidationError("Такої події немає у списку.")
        if event["seats_left"] <= 0:
            raise ValidationError(
                f"На «{event['title']}» вільних місць немає. Оберіть іншу подію."
            )
