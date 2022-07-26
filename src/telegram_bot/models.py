from django.db import models


class ChatId(models.Model):
    chat_id = models.CharField(max_length=30, blank=True, verbose_name='id чата в телеграмме')
