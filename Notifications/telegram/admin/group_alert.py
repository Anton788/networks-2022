import telebot


ADMIN_BOT_TOKEN = "<ADMIN_BOT_TOKEN>"
chat_id = -1


def get_admin_telegram_bot():
    return telebot.TeleBot(ADMIN_BOT_TOKEN)


def alert_admin_tg_message(text, parse_mode='Markdown'):
    try:
        bot = get_admin_telegram_bot()
        text = text.strip()
        bot.send_message(chat_id, text=text, parse_mode=parse_mode)
    except:
        print("Error message")
