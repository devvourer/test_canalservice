from django.core.management.base import BaseCommand

from src.sheets.service import SheetServiceCommand, CurrencyService


class Command(BaseCommand):
    help = 'Start sheet services'

    def handle(self, *args, **options):
        # Записываем курс доллара к рублю
        currency_service = CurrencyService()
        currency_service.set_currency()

        # Заполняем данные в бд
        service = SheetServiceCommand()
        service.get_base_values()

