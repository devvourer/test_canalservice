from decimal import Decimal

from .models import Currency


def convert_to_rub(number: Decimal) -> Decimal:
    rate = Currency.objects.get(name='RUB').currency_to_usd
    return number * rate


def get_formatted_date(date: str) -> str:
    date = date.split('.')
    date.reverse()
    return f'{date[0]}-{date[1]}-{date[2]}'
