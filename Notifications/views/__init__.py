from django.shortcuts import get_object_or_404
from .system_notifications import *

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication

from APIBackendService.views import AppUsersAPIView, BaseAppAPIView
from Notifications.constants import TELEGRAM_BOT_TOKEN, ADMIN_INFO
from Orders.models import OrderChain
from Organizations.models import Company

import requests
import json
from telebot.types import Message, Update, KeyboardButton

from Users.models import User, UserCompanyRelation
from Notifications.telegram.functions import send_request_for_chain, accept_chain, reject_chain

from django.views.generic import CreateView
from Notifications.service import send
from django.utils.crypto import get_random_string
import datetime
from .telegram_admin import ReceiveTelegramAdminNotificationsView
from ..telegram import alert_admin_tg_message

TELEGRAM_URL = "https://api.telegram.org/bot"
from Notifications.constants import TELEGRAM_BOT_TOKEN as TOKEN
#TOKEN = "5058184076:AAE--c4qZMQgcRHumle5k2JP048fAgkdsHQ"

from APIBackendService.views import AppCompanyAPIView

from Users.constants.user_organization_role import OWNER, MANAGER, STAFF

import telebot
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardButton
from django.views.decorators.csrf import csrf_exempt
from Notifications.models import TelegramMessage, OrderChainTelegramNotification


# https://api.telegram.org/bot<token>/setWebhook?url=<url>(==https://neochainer.space/api/notifications/telegram/receive/)



bot = telebot.TeleBot(TOKEN)


'''@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Здравствуйте!\nЯ помогаю работать с цепями поставок")'''

    
@bot.message_handler(commands=['start'])
def add_account_message(message):
    bot.send_message(message.chat.id, "Здравствуйте!\nЯ помогаю работать с цепями поставок")
    chat_id = message.chat.id
    t_message = message.text
    user_queryset = User.objects.filter(telegram_id=chat_id)
    in_base = user_queryset.exists()
    contact = message.contact
    
    if in_base:
        bot.send_message(chat_id, "Аккаунт уже в базе. Уведомления о заявках включены.")
    else:

        if contact:
            alert_admin_tg_message(f"Contacts: {contact}")
            # phone_number: str = t_message["contact"]["phone_number"]
            phone_number: str = message.contact.phone_number
            queryset = User.objects.filter(
                telephone=phone_number,
            )
            if queryset.exists():
                user = queryset.first()
                user.telegram_id = chat_id
                user.save()
                bot.send_message(chat_id, "Аккаунт подтвержден ✅")
            else:
                bot.send_message(
                    chat_id,
                    "Аккаунт с таким номером не найден.\n\n"
                    "Зарегистрируйтесь на [сайте компании](https://supplydirector.ru) и "
                    "заполните свой номер телефона.")
        else:

            reply_markup = ReplyKeyboardMarkup(
                one_time_keyboard=True,
                resize_keyboard=True,
            )
            reply_markup.row_width = 1
            reply_markup.add(KeyboardButton(
                "Отправить телефон",
                request_contact=True
            ),)

            bot.send_message(
                chat_id,
                "Чтобы использовать бота, надо присоединить твой аккаунт. "
                "Подтверди свой номер телефона по кнопке.",
                reply_markup=reply_markup,
            )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    
    telegram_id = call.message.chat.id
    message_id = call.message.message_id
    tele_message = get_object_or_404(TelegramMessage, 
                                     chat_id=telegram_id,
                                     message=message_id)
    chain_message = get_object_or_404(OrderChainTelegramNotification,
                                      message=tele_message)
    chain = chain_message.chain
        
    if call.data == "accept_chain":
        accept_chain(chain)
        
    elif call.data == "reject_chain":
        reject_chain(chain)


@bot.message_handler(content_types=['contact'])
def message_common(message):
    # alert_admin_tg_message(f"Get Contacts")
    # message = call.message
    chat_id = message.chat.id

    # contact = message.contact

    # alert_admin_tg_message(f"Contacts: {contact}")
    # phone_number: str = t_message["contact"]["phone_number"]
    phone_number: str = message.contact.phone_number
    queryset = User.objects.filter(
        telephone=phone_number,
    )
    if queryset.exists():
        user = queryset.first()
        user.telegram_id = chat_id
        user.save()
        bot.send_message(chat_id, "Аккаунт подтвержден ✅")
    else:
        bot.send_message(
            chat_id,
            "Аккаунт с таким номером не найден.\n\n"
            "Зарегистрируйтесь на [сайте компании](https://supplydirector.ru) и "
            "заполните свой номер телефона."
        )


class ReceiveTelegramNotificationsView(BaseAppAPIView):
    """
    View for receiving notifications from telegram's servers (api.telegram.org)
    """

    authentication_classes = []
    permission_classes = []
    

    def post(self, request):

        json_string = json.dumps(json.loads(request.body))
        update = Update.de_json(json_string)
        bot.process_new_updates([update])

        return Response(200)



@bot.message_handler(func=lambda m: True)
def answer_any_message(message):
    chat_id = message.chat.id
    user_queryset = User.objects.filter(telegram_id=chat_id)
    in_base = user_queryset.exists()

    if in_base:
        bot.send_message(chat_id, "Аккаунт уже в базе. Ждите уведомлений о новых заказах!")
    else:
        bot.send_message(chat_id, "Аккаунт не обнаружен :(\n"
                                  "Чтобы добавить аккаунт в базу, нажмите /start")

























'''

class ReceiveTelegramNotificationsView(APIView):
    """
    View for receiving notifications from telegram's servers (api.telegram.org)
    """
    
    
    def post(self, request):
        """
        message:
            [message_id]
            [text]
            from -> User
                [id]

            chat -> Chat
                [id]

            contact -> Contact
                [phone_number] - string
                [first_name] - string
                [last_name] - string
        """
        t_data = json.loads(request.body)
        t_message: dict = t_data["message"]
        t_chat = t_message["chat"]
        # t_from = t_message["from"]
        # sender_id = t_from["id"]
        chat_id = t_chat["id"]
        user_queryset = User.objects.filter(telegram_id=chat_id)
        in_base = user_queryset.exists()
        # self.send_message(chat_id, "CHECK")
        
        
        if in_base:
            self.send_message(chat_id, "Аккаунт уже в базе. Уведомления о заявках включены.")
        else:
            # self.send_message(chat_id, f"Ищем в базе...")
            if "contact" in t_message.keys():

                phone_number: str = t_message["contact"]["phone_number"]
                queryset = User.objects.filter(
                    telephone=phone_number,
                )
                # self.send_message(
                #     chat_id,
                #     f"Спасибо! Твой номер {phone_number}")
                if queryset.exists():
                    user = queryset.first()
                    user.telegram_id = chat_id
                    user.save()
                    self.send_message(chat_id, "Аккаунт подтвержден ✅")
                else:
                    self.send_message(
                        chat_id,
                        "Аккаунт с таким номером не найден.\n\n"
                        "Зарегистрируйтесь на [сайте компании](https://neochainer.space/) и "
                        "заполните свой номер телефона.")
            else:
                reply_markup = {
                    "keyboard": [[{
                        "text": "Отправить телефон",
                        "request_contact": True,
                    }]],
                    "one_time_keyboard": True,
                    "resize_keyboard": True,
                }
                self.send_message(
                    chat_id,
                    "Чтобы использовать бота, надо присоединить твой аккаунт. "
                    "Подтверди свой номер телефона по кнопке.",
                    reply_markup=reply_markup,
                )

        # msg = "Unknown command"
        # self.send_message(msg, t_chat["id"])

        return Response({"ok": "POST request processed"})

    @staticmethod
    def send_message(chat_id, message, reply_markup=None):
        answer_data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            # **kwargs,
        }
        if reply_markup is None:
            reply_markup = {
                "remove_keyboard": True,
            }
        answer_data["reply_markup"] = json.dumps(reply_markup)
        # reply_markup = {
        #     "remove_keyboard": True,
        # }
        # if "reply_markup" in kwargs.keys():
        #     reply_markup = kwargs["reply_markup"]
        # data = {
        #     "reply_markup": reply_markup,
        #     **kwargs,
        # }
        response = requests.post(
            f"{TELEGRAM_URL}{TELEGRAM_BOT_TOKEN}/sendMessage", data=answer_data
        )'''
    


from django.core.mail import send_mail
from django.core import mail


'''class SendEmailAboutNewUserView(APIView):

    def post(self, request):
        user_email = request.data.get('user_email')
        login = request.data.get('login')
        password = request.data.get('password')
        text = f"Здравствуйте!\nВ системе зарегистрирован новый пользователь\nЛогин: {login}\nПароль: {password}"
        send(user_email,
             subject="Новый корпоративный пользователь",
             text=text)
        return Response({"ok": "POST request processed"})'''


class SendRequestForChainView(APIView):

    def post(self, request):
        chain_id = request.data.get("chain")
        chain = get_object_or_404(OrderChain, id=chain_id)
        link = request.data.get("link")
        send_request_for_chain(chain, link)
        return Response({"ok": "POST request processed"})


class AcceptChainView(APIView):

    def post(self, request):
        chain_id = request.data.get("chain")
        chain = get_object_or_404(OrderChain, id=chain_id)
        accept_chain(chain)
        return Response({"ok": "POST request processed"})


class RejectChainView(AppUsersAPIView):
    

    def post(self, request):
        chain_id = request.data.get("chain")
        chain = get_object_or_404(OrderChain, id=chain_id)
        reject_chain(chain)
        return Response({"ok": "POST request processed"})
    
    
    
    
    
    
    
    
    
'''# NEW VIEWS FROM HERE
import time

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url="https://supplydirector.ru/api/notifications/telegram/user/receive/")


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Приветики ;)")
    
class ReceiveTelegramUserNotificationsView(BaseAppAPIView):
    """
    View for receiving notifications from telegram's servers (api.telegram.org)
    """

    authentication_classes = []
    permission_classes = []
    

    def post(self, request):
        print("AAAAAAA")
        json_string = json.dumps(json.loads(request.body))
        update = Update.de_json(json_string)
        bot.process_new_updates([update])

        return Response(200)'''

    
    
    


