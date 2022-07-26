from django.utils.timezone import datetime

from core.celery import app
from src.sheets.models import Order
from .models import ChatId
from .bot import bot


@app.task
def send_messages() -> None:
    chats = ChatId.objects.all()
    orders = Order.objects.filter(delivery_date__lte=datetime.today())

    for chat in chats:
        for order in orders:
            bot.send_message(chat.chat_id, f"Заказ: {order.order_number}, {order.cost_rub}руб, {order.delivery_date}"
                                           f"- срок поставки истек")

