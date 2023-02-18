from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from account.models import Profile


# Create your models here.
class House(models.Model):
    name = models.CharField("Название", max_length=150, null=True)
    address = models.CharField("Адрес", max_length=150, null=True)
    image1 = models.ImageField("Изображение #1. Размер: (522x350)", upload_to='house/', null=True, blank=True)
    image2 = models.ImageField("Изображение #2. Размер: (248x160)", upload_to='house/', null=True, blank=True)
    image3 = models.ImageField("Изображение #3. Размер: (248x160)", upload_to='house/', null=True, blank=True)
    image4 = models.ImageField("Изображение #4. Размер: (248x160)", upload_to='house/', null=True, blank=True)
    image5 = models.ImageField("Изображение #5. Размер: (248x160)", upload_to='house/', null=True, blank=True)
    users = models.ManyToManyField(Profile)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('admin:detail_house',
                       args=[self.id])


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


class Gallery(models.Model):
    image = models.ImageField(upload_to='gallery/')
    additional = models.BooleanField(default=True)


class Document(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    file = models.FileField(upload_to='documents/', null=True, blank=True)


class Info(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    extra_title = models.CharField(max_length=100, null=True, blank=True)
    extra_description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='avatar/', null=True, blank=True)
    seo = models.ForeignKey(SeoText, on_delete=models.SET_NULL, null=True)


class ServicePage(models.Model):
    seo = models.ForeignKey(SeoText, on_delete=models.SET_NULL, null=True)


class ServiceBlock(models.Model):
    name = models.CharField( max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='customer_services/')


class ContactPage(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    link_commercial = models.URLField(max_length=200, null=True, blank=True)
    fullname = models.CharField(max_length=200, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    e_mail = models.EmailField(max_length=30, null=True, blank=True)
    map = models.TextField(null=True, blank=True)
    seo = models.ForeignKey(SeoText, on_delete=models.SET_NULL, null=True)


class Invite(models.Model):
    phone = models.CharField('Телефон', max_length=15)
    mail = models.EmailField(max_length=30, null=True, blank=True)