from random import choice
from telebot.types import Message


def gratitude_answer(bot, message: Message, parse_mode="Markdown"):
    bot.send_message(
        message.chat.id,
        f"🇷🇺 *Служу России!* 🇷🇺",
        parse_mode=parse_mode)


def get_on_edit_message_reply(username):
    ustr = f"@{username}"
    answers = [
        f"Ну нифига себе. А чего редачим, {ustr}?",
        f"Докладываю. {ustr} редактирует сообщения.",
        f"А мы типа не заметили, {ustr}?",
        f"Алё, {ustr}",
        f"Ну хорош уже, {ustr}",
        f"{ustr} ай-ай-ай",
    ]
    return choice(answers)
