from rest_framework.response import Response

from APIBackendService.views import BaseAppAPIView
from Notifications.constants import ADMIN_INFO
from Notifications.telegram import get_admin_telegram_bot, alert_admin_tg_message
from Notifications.telegram.admin.handlers import check_admin_sender, is_gratitude, gratitude_answer, \
    get_on_edit_message_reply
import json
from telebot.types import Message, Update

bot = get_admin_telegram_bot()


@bot.message_handler(commands=['start'], func=check_admin_sender)
def start_message(message):
    bot.send_message(message.chat.id, "Здравствуй, товарищ!\nЯ помогаю админам.")


@bot.message_handler(commands=['base_stat'], func=check_admin_sender)
def base_stat_message(message):
    bot.send_message(message.chat.id,
                     f"*В разработке*",
                     parse_mode="Markdown")


@bot.message_handler(func=lambda x: check_admin_sender(x) and is_gratitude(x.text))
def gratitude_reply_message(message):
    gratitude_answer(bot, message)


@bot.message_handler(func=check_admin_sender)
def base_message(message: Message):
    # print("GET START")
    # message.sticker
    pass

    # if message.reply_to_message:
    #     try:
    #         bot.send_message(message.chat.id, f"*Ответ на сообщение*\n{message.reply_to_message.text}",
    #                          parse_mode="Markdown")
    #     except:
    #         bot.send_message(message.chat.id, f"*Ответ на сообщение*\n_Без текста_",
    #                          parse_mode="Markdown")
    # else:
    #     bot.send_message(message.chat.id, f"*Твой текст*: {message.text}", parse_mode="Markdown")


@bot.edited_message_handler(func=check_admin_sender)
def edit_message(message: Message):
    text = get_on_edit_message_reply(message.from_user.username)
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


class ReceiveTelegramAdminNotificationsView(BaseAppAPIView):
    """
    View for receiving notifications from telegram's servers (api.telegram.org)
    """

    authentication_classes = []
    permission_classes = []
    

    def post(self, request):
        # alert_admin_tg_message("Получил")

        json_string = json.dumps(json.loads(request.body))
        update = Update.de_json(json_string)
        bot.process_new_updates([update])

        return Response(200)
