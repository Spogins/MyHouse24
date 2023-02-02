from django.conf import settings
from django.db import models

# Create your models here.


class Owner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    patronymic = models.CharField('Отчество', max_length=30)
    image = models.ImageField('Сменить изображение', upload_to='owners/', null=True, blank=True)
    birthday = models.DateField('Дата Рождения', null=True)
    info = models.TextField('О владельце (заметки)')
    phone = models.CharField('Телефон', max_length=15)
    viber = models.CharField('Viber', max_length=15)

    class Status(models.TextChoices):
        active = 'Активен'
        new = 'Новый'
        disabled = 'Отключен'

    status = models.CharField("Статус", choices=Status.choices, max_length=20, default='Новый')

    @property
    def fullname(self):
        return f"{self.user.last_name} {self.user.first_name} {self.patronymic}"


class User(models.Model):
    pass





