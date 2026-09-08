import logging

import requests
from django.conf import settings
import environ
from pathlib import Path

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
env.read_env(BASE_DIR / ".env")
logger = logging.getLogger(__name__)


def send_booking_notification(booking):
    token = env("TELEGRAM_BOT_TOKEN", default="")
    chat_id = env("TELEGRAM_MANAGER_CHAT_ID", default="")
    if not token or not chat_id:
        logger.warning("TELEGRAM_BOT_TOKEN / TELEGRAM_MANAGER_CHAT_ID не задані — сповіщення не надіслано.")
        return

    tour = booking.tour
    nights = tour.nights if tour else booking.nights
    meal_display = tour.get_meal_type_display() if tour else (
        booking.get_meal_type_display() if booking.meal_type else None
    )

    lines = [
        "🆕 Нова заявка на тур",
        f"Тур: {booking.tour}" if booking.tour_id else "Тур: не вказано",
        f"К-сть дорослих: {booking.adults_count}",
        f"Діти: {'так' if booking.children else 'ні'}",
        f"К-сть ночей: {nights}" if nights else "К-сть ночей: не вказано",
        f"Тип харчування: {meal_display}" if meal_display else "Тип харчування: не вказано",
        f"Ім'я: {booking.full_name}",
        f"Телефон: {booking.phone}",
        f"Email: {booking.email or '—'}",
    ]

    if booking.preferred_date_from or booking.preferred_date_to:
        date_from = booking.preferred_date_from.strftime("%d.%m.%Y") if booking.preferred_date_from else "?"
        date_to = booking.preferred_date_to.strftime("%d.%m.%Y") if booking.preferred_date_to else "?"
        lines.append(f"Бажана дата: {date_from} – {date_to}")

    if booking.comment:
        lines.append(f"Коментар: {booking.comment}")

    text = "\n".join(lines)

    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=5,
        )
    except requests.RequestException:
        logger.exception("Не вдалося надіслати повідомлення в Telegram")
