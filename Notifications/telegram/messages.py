import os
import telebot

# TOKEN = ""


def alert_message(text):
    try:
        pass
        # bot = telebot.TeleBot(TOKEN)
        # bot.send_message(chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        print("Error send telegram message:", e)
