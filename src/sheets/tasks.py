from core.celery import app

from .service import SheetService, CurrencyService


@app.task
def get_data_from_sheet() -> None:
    service = SheetService()
    service.set_values_to_db()


@app.task
def get_currency_rate() -> None:
    service = CurrencyService()
    service.set_currency()


app.conf.beat_schedule = {
    'get-data-from-sheet': {
        'task': 'src.sheets.tasks.get_data_from_sheet',
        'schedule': 10.0
    },
    'send-messages': {
        'task': 'src.telegram_bot.tasks.send_messages',
        'schedule': 350.0,
    },
    'get-currency-rate': {
        'task': 'src.sheets.tasks.get_currency_rate',
        'schedule': 86400.0,
    }
}
