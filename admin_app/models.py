from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class House(models.Model):
    pass


class SeoText(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    keywords = models.TextField()


class Unit(models.Model):
    name = models.CharField(max_length=10)

    # class Meta:
    #     unique_together = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=20)
    unit = models.ForeignKey(Unit, on_delete=models.RESTRICT, null=True, blank=True)
    show = models.BooleanField(default=False)

    # class Meta:
    #     unique_together = ['name']

    def __str__(self):
        return self.name


class Tariff(models.Model):
    name = models.CharField('Название тарифа', max_length=20)
    description = models.TextField('Описание')
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class TariffService(models.Model):
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    price = models.FloatField('Цена')
    currency = models.CharField('Валюта', default='грн', max_length=5)


class Role(models.Model):
    name = models.CharField(max_length=15, null=True, blank=True)
    statistic = models.BooleanField(default=False)
    cash_box = models.BooleanField(default=False)
    invoice = models.BooleanField(default=False)
    personal_account = models.BooleanField(default=False)
    apartment = models.BooleanField(default=False)
    owner = models.BooleanField(default=False)
    house = models.BooleanField(default=False)
    message = models.BooleanField(default=False)
    application = models.BooleanField(default=False)
    meter = models.BooleanField(default=False)
    site_management = models.BooleanField(default=False)
    service = models.BooleanField(default=False)
    tariff = models.BooleanField(default=False)
    role = models.BooleanField(default=False)
    users = models.BooleanField(default=False)
    requisites = models.BooleanField(default=False)


class PaymentDetails(models.Model):
    name = models.CharField(max_length=15, null=True)
    description = models.TextField(null=True)


class PaymentItems(models.Model):
    name = models.CharField(max_length=35, null=True)

    class Status(models.TextChoices):
        income = 'Приход', _('Приход')
        rate = 'Расход', _('Расход')

    status = models.CharField(choices=Status.choices, max_length=20, default='Приход')


class MainPage(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    show_link = models.BooleanField(default=True)
    seo = models.ForeignKey(SeoText, on_delete=models.SET_NULL, null=True)


class Slide(models.Model):
    image = models.ImageField(upload_to='slides/', null=True, blank=True)


class NearBlock(models.Model):
    image = models.ImageField(upload_to='near/', null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(max_length=300, null=True, blank=True)

