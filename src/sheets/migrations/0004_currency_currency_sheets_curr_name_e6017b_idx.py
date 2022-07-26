# Generated by Django 4.0.6 on 2022-07-25 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sheets', '0003_alter_order_delivery_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='Имя валюты')),
                ('currency_to_usd', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Курс валюты к доллару')),
            ],
        ),
        migrations.AddIndex(
            model_name='currency',
            index=models.Index(fields=['name'], name='sheets_curr_name_e6017b_idx'),
        ),
    ]