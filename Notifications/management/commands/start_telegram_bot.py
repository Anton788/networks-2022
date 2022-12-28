from django.core.management.base import BaseCommand, CommandError

import telebot
from telebot import types

from Users.models import User
from Notifications.constants import TELEGRAM_BOT_TOKEN as TOKEN


class Command(BaseCommand):
    def handle(self, *args, **options):
        bot = telebot.TeleBot(TOKEN)
        
        #@bot.message_handler(commands=['start'])
        #def start_message(message):
            #bot.send_message(message.chat.id, "bonjour")
        
        bot.set_webhook(url="https://supplydirector.ru/api/notifications/telegram/receive/")
        #bot.infinity_polling()
