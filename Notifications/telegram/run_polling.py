import os, django
import telebot

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dtb.settings')
# django.setup()

from Notifications.constants import TELEGRAM_BOT_TOKEN as TOKEN


if __name__ == "__main__":
    bot = telebot.TeleBot(TOKEN)
    bot.remove_webhook()

    # print(bot.__dict__)

    @bot.message_handler(commands=['start'])
    def start_message(message):
        print("GET START")
        bot.send_message(message.chat.id, "Привет ✌")

    bot.infinity_polling()
