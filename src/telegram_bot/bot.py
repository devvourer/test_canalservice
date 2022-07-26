import telebot

from django.conf import settings

from .models import ChatId

token = settings.TELEGRAM_BOT_TOKEN
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start_message(message):
    ChatId.objects.create(chat_id=message.chat.id)  # записываем id чата в бд
    bot.send_message(message.chat.id, 'После окончания срока поставки заказов'
                                      ' будут посылаться сообщения, Удачного дня!')

