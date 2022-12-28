from telebot.types import Message

from Notifications.constants import ADMIN_TG_IDS


def check_admin_sender(message: Message):
    return message.from_user.id in ADMIN_TG_IDS


def is_gratitude(text: str):
    try:
        text = text.lower().strip()
        return text.startswith("спасибо") or text.startswith("благодарю") \
               or text.startswith("объявляется благодарность")
    except:
        return False
