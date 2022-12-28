import django
from django.shortcuts import get_object_or_404

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

import urllib
import os, sys
from os.path import dirname

SCRIPT_DIR = dirname(os.path.abspath(__file__))
sys.path.append(dirname(dirname(SCRIPT_DIR)))

from Users.models import UserCompanyRelation, UserFactoryRelation
from Orders.models import ProductRequestImage, OrderChain
from Notifications.models import TelegramMessage, OrderChainTelegramNotification

from django.views.decorators.csrf import csrf_exempt
from Notifications.constants import TELEGRAM_BOT_TOKEN as TOKEN



def markup_chain_request(link):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Принять", callback_data="accept_chain"),
               InlineKeyboardButton("Отклонить", callback_data="reject_chain"),
               InlineKeyboardButton("Подробнее", callback_data="view_chain",
                                    url=link))
    return markup


@csrf_exempt
def send_request_for_chain(chain, link):
    
    bot = telebot.TeleBot(TOKEN)

    company_executor = chain.company_executor
    factory_executor = chain.factory_executor

    product_request = chain.product_request
    product = product_request.product
    description = product_request.description
    if product:
        request_text = " " + product.name
    elif description:
        request_text = " " + description
        if len(request_text) > 31:
            request_text = request_text[:31] + "..."
    else:
        request_text = ""

    preferable_time = product_request.preferable_time
    preferable_price = product_request.preferable_price
    amount = product_request.amount

    details = ""
    if preferable_time:
        details += f"Пожелание заказчика по максимальному времени исполнения заказа: {preferable_time}. "
    if preferable_price:
        details += f"Пожеление заказчика по максимальной стоимости заказа: {preferable_price}. "

    customer = product_request.customer

    images = ProductRequestImage.objects.filter(request=product_request)

    if company_executor:
        users_relations = UserCompanyRelation.objects.filter(company=company_executor,
                                                             ordering_permission=True)
        for user_relation in users_relations:
            user = user_relation.user
            telegram_id = user.telegram_id
            if telegram_id:
                message = bot.send_message(
                    telegram_id,
                    f'Вам поступил заказ _{request_text}_. ' + details,
                    reply_markup=markup_chain_request(link=link),
                    parse_mode='Markdown',
                )

                tele_message = TelegramMessage.objects.create(
                    user=user,
                    chat_id=telegram_id,
                    message=message.id,
                )
                tele_message.save()
                chain_message = OrderChainTelegramNotification.objects.create(
                    chain=chain,
                    message=tele_message,
                )
                chain_message.save()

                for url in images:
                    # url = image.link
                    f = open('out.jpg', 'wb')
                    f.write(urllib.request.urlopen(url).read())
                    f.close()

                    img = open('out.jpg', 'rb')
                    message = bot.send_photo(telegram_id, img)
                    img.close()

                    tele_message = TelegramMessage.objects.create(user=user,
                                                                  chat_id=telegram_id,
                                                                  message=message.id,
                                                                  )
                    tele_message.save()
                    chain_message = OrderChainTelegramNotification.objects.create(
                        chain=chain,
                        message=tele_message,
                    )
                    chain_message.save()


def accept_chain(chain):
    bot = telebot.TeleBot(TOKEN)

    company_executor = chain.company_executor
    factory_executor = chain.factory_executor

    time = chain.time
    price = chain.price

    details = ""
    if time:
        details += f"Предполагаемое время исполнения заказа: {time}. "
    if price:
        details += f"Стоимость заказа: {price}. "

    product_request = chain.product_request
    product = product_request.product
    description = product_request.description
    if product:
        request_text = " " + product.name
    elif description:
        request_text = " " + description
        if len(request_text) > 31:
            request_text = request_text[:31] + "..."
    else:
        request_text = ""

    customer = product_request.customer
    # user = product_request.user

    customer_users_relations = UserCompanyRelation.objects.filter(company=customer,
                                                                  ordering_permission=True)

    for user_relation in customer_users_relations:
        user = user_relation.user
        telegram_id = user.telegram_id
        if telegram_id:
            message = bot.send_message(telegram_id,
                                       f'Ваш заказ_{request_text}_ принят. ' + details,
                                       parse_mode='Markdown',
                                       )

    notifications = OrderChainTelegramNotification.objects.filter(chain=chain)
    for count, notification in enumerate(notifications):
        message = notification.message
        chat_id = message.chat_id
        message_id = message.message
        if count == 0:

            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text=f"Заказ _{request_text}_ принят" + details,
                                  parse_mode='Markdown', )

            other_potential_chains = OrderChain.objects.filter(product_request=product_request).exclude(id=chain.id)
            if other_potential_chains.exists():
                for other_chain in other_potential_chains:
                    # message = bot.send_message(telegram_id,
                    # str(other_chain.id),
                    # )
                    notification = get_object_or_404(OrderChainTelegramNotification, chain=other_chain)
                    message = notification.message
                    chat_id = message.chat_id
                    message_id = message.message
                    try:
                        bot.delete_message(chat_id, message_id)
                        message.delete()
                    except:
                        pass
        else:
            try:
                bot.delete_message(chat_id, message_id)
                message.delete()
            except:
                pass


@csrf_exempt
def reject_chain(chain):
    bot = telebot.TeleBot(TOKEN)

    company_executor = chain.company_executor
    factory_executor = chain.factory_executor

    product_request = chain.product_request
    product = product_request.product
    description = product_request.description
    if product:
        request_text = " " + product.name
    elif description:
        request_text = " " + description
        if len(request_text) > 31:
            request_text = request_text[:31] + "..."
    else:
        request_text = ""

    preferable_time = product_request.preferable_time
    preferable_price = product_request.preferable_price
    amount = product_request.amount

    details = ""
    if preferable_time:
        details += f"Ваши пожелания по максимальному времени исполнения заказа: {preferable_time}. "
    if preferable_price:
        details += f"Ваши пожелания по максимальной стоимости заказа: {preferable_price}. "
    # request_text = product_request.request
    # if len(request_text)>20:
    # request_text = request_text[:20] + "..."

    customer = product_request.customer
    # user = product_request.user

    customer_users_relations = UserCompanyRelation.objects.filter(company=customer,
                                                                  ordering_permission=True)
    for user_relation in customer_users_relations:
        user = user_relation.user
        telegram_id = user.telegram_id
        if telegram_id:
            message = bot.send_message(telegram_id,
                                       f'Одна из компаний отклонила ваш заказ_{request_text}_. ' + details,
                                       parse_mode='Markdown',
                                       )


def file_processing_status(processing, success, detail=None, link=None):
    def gen_markup():
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(InlineKeyboardButton("Подробнее",
                                        callback_data="file_rejected_details",
                                        url=link))
        return markup


    bot = telebot.TeleBot(TOKEN)

    factory = processing.factory
    company = processing.company
    name = processing.name

    if success:
        message_text = f"Файл _{name}_ успешно добавлен!"
    else:
        message_text = f'При добавлении файла _{name}_ возникла ошибка: _{detail}_. Нажмите "Подробнее", чтобы посмотреть детали ошибки'

    if factory:
        factory_users_relations = UserFactoryRelation.objects.filter(factory=factory,
                                                                     product_interaction_permission=True)
        for user_relation in factory_users_relations:
            user = user_relation.user
            telegram_id = user.telegram_id
            if telegram_id:
                message = bot.send_message(telegram_id,
                                           message_text,
                                           parse_mode='Markdown',
                                           reply_markup=gen_markup()
                                           )

    elif company:
        company_users_relations = UserCompanyRelation.objects.filter(
            company=company,
            product_interaction_permission=True)
        for user_relation in company_users_relations:
            user = user_relation.user
            telegram_id = user.telegram_id
            if telegram_id:
                message = bot.send_message(telegram_id,
                                           message_text,
                                           parse_mode='Markdown',
                                           reply_markup=gen_markup()
                                           )
