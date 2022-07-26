from django.core.management import BaseCommand

from src.telegram_bot.bot import bot


class Command(BaseCommand):
    help = 'Start bot polling'

    def handle(self, *args, **options):
        bot.infinity_polling()

