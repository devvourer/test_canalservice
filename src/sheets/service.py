import httplib2
import requests
import xmltodict

from typing import Union
from lxml import etree
from decimal import Decimal
from apiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

from django.conf import settings
from django.utils.timezone import datetime

from .models import Order, Currency
from .utils import convert_to_rub, get_formatted_date


class SheetService:
    """ Класс для взаимодействия с google sheet
    Есть таблица(1) в которой записываются/редактируются записи,
    в этой таблице(1) написан скрипт Google apps script-который записывает в другую таблицу(2)
    новые или отредактированные записи. Записи в таблице(2) удаляются раз в минуту (там так же написан скрипт,
                                                                                    который удаляет все записи)
    Метод: set_values_to_db - получает данные с таблицы(2) где хранятся
                             отредактированные или новые записи и сохраняет их в бд

    Примечание: В таблице можно сделать вебхук на изменение/редактирование,
     но реализовать его не удалось так-как нет сервера и проект должен работать на локалке
    """

    # Файл необходимый для получения доступа к google sheet документу
    credentials_file = str(settings.BASE_DIR) + '/creds.json'
    # ID Google Sheets документа для таблицы(2)
    spreadsheet_id = '193YT2mL_73OrHERDAU-Ho3J179JIzsDgV5l42eFqeTY'

    def __init__(self):
        self.service = self._get_service

    @property
    def _get_credentials(self):
        return ServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_file,
            ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']
        )

    @property
    def _get_service(self):
        # Авторизуемся и получаем service — экземпляр доступа к API
        credentials = self._get_credentials
        https_auth = credentials.authorize(httplib2.Http())
        return discovery.build('sheets', 'v4', http=https_auth)

    def get_values(self) -> Union[list, None]:
        """ Получаем данные с таблицы """
        sheet = self.service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range='A1:D'
        ).execute()
        try:
            values = result['values']
            return values
        except KeyError:
            return None

    def set_values_to_db(self) -> None:
        """ Получаем данные с таблицы, и проверяем есть ли такая запись в бд,
        если нет создаем, если да то обновляем значения"""
        values = self.get_values()

        orders_bulk_update = []
        orders_bulk_create = []
        if values:
            for i in values:
                if len(i) == 4 and i[3] != '':  # Проверяем целостность записи
                    # получение суммы в рублях
                    cost_rub = convert_to_rub(Decimal(i[2].replace(',', '.')))
                    # получаем отформатированную дату YYYY-MM-DD
                    date = get_formatted_date(i[3])
                    try:
                        order = Order.objects.get(
                            order_pk=i[0],
                            order_number=i[1]
                        )
                        order.cost_usd = i[2]
                        order.cost_rub = cost_rub
                        order.delivery_date = date
                        orders_bulk_update.append(order)
                    except Order.DoesNotExist:
                        order = Order(order_pk=i[0],
                                      order_number=i[1],
                                      cost_usd=i[2],
                                      cost_rub=cost_rub,
                                      delivery_date=date)
                        orders_bulk_create.append(order)
        if orders_bulk_create:
            Order.objects.bulk_create(orders_bulk_create)
        if orders_bulk_update:
            Order.objects.bulk_update(orders_bulk_update, fields=['cost_usd', 'cost_rub', 'delivery_date'])


class SheetServiceCommand(SheetService):
    """ Класс для заполнения бд при запуске """
    spreadsheet_id = '1rgNWTlZ95boWNA_BmSx1cTViIa5epI1XSXkb9QVCNMg'

    def get_base_values(self) -> None:
        """ Получаем данные с основной таблицы и записываем значения в бд.
            Этот метод используется при вызове команды python manage.py sheets
        """
        values = self.get_values()
        orders_bulk_create = []
        for i in values:
            try:
                if not i[0] == '№' and len(i) == 4:  # Если запись начинается с № - пропустить итерацию
                    # так-как в таблице первой записью идет название колонок

                    cost_rub = convert_to_rub(Decimal(i[2].replace(',', '.')))
                    date = get_formatted_date(i[3])  # получаем отформатированную дату YYYY-MM-DD
                    orders_bulk_create.append(Order(
                        order_pk=i[0],
                        order_number=i[1],
                        cost_usd=i[2],
                        cost_rub=cost_rub,
                        delivery_date=date,
                    ))
            except IndexError:
                continue
        try:
            Order.objects.bulk_create(orders_bulk_create)
        except Exception:
            print('Записи уже существуют')


class CurrencyService:
    """ Сервис для взаимодействия с сайтом https://www.cbr.ru/
        set_currency - получает курс доллара к рублю и записывает значение в бд
    """
    bank_url = 'https://www.cbr.ru/scripts/XML_dynamic.asp?'

    @property
    def _get_url(self):
        today = datetime.today().strftime('%d/%m/%Y')
        return self.bank_url + f"date_req1={today}&date_req2={today}&VAL_NM_RQ=R01235"

    @staticmethod
    def get_xml_to_dict(xml) -> dict:
        if type(xml) == bytes:
            xml_to_dict = xmltodict.parse(xml, encoding='windows-1251')
        else:
            xml_bytes = etree.tostring(xml, encoding='windows-1251')
            xml_to_dict = xmltodict.parse(xml_bytes, encoding='windows-1251')
        return xml_to_dict

    def set_currency(self) -> None:
        url = self._get_url
        response = requests.get(url)
        # превращаем xml в словарь так как ответ от цб приходит в xml
        data = self.get_xml_to_dict(etree.XML(response.content))
        # достаем значение курса к рублю
        rate = data['ValCurs']['Record']['Value']
        # обновляем значение курса в базе данных
        currency, created = Currency.objects.get_or_create(name='RUB')
        currency.currency_to_usd = Decimal(rate.replace(',', '.'))
        currency.save()

