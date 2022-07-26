from django.db import models


class Order(models.Model):
    order_pk = models.IntegerField(primary_key=True)
    order_number = models.CharField(max_length=50, blank=True, verbose_name='Номер заказа')
    cost_usd = models.DecimalField(max_digits=8, decimal_places=2, null=True, verbose_name='Стоимость в долларах')
    cost_rub = models.DecimalField(max_digits=8, decimal_places=2, null=True, verbose_name='Стоимость в рублях')
    delivery_date = models.DateField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['order_pk', 'order_number']),
        ]


class Currency(models.Model):
    name = models.CharField(max_length=20, verbose_name='Имя валюты')
    currency_to_usd = models.DecimalField(max_digits=10, decimal_places=2,
                                          verbose_name='Курс валюты к доллару',
                                          null=True)

    class Meta:
        indexes = [
            models.Index(fields=['name'])
        ]