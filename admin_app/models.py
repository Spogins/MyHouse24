from django.db import models
from django.db.models import Max, Min, Sum
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
import logging
from account.models import Profile, Owner

# Get an instance of a logger
logger = logging.getLogger(__name__)

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


class Section(models.Model):
    name = models.CharField("Название", max_length=150)
    house = models.ForeignKey(House, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Level(models.Model):
    name = models.CharField("Название", max_length=150)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='house_level')

    def __str__(self):
        return self.name


class Flat(models.Model):
    number = models.CharField("Номер квартиры", max_length=10)
    area = models.FloatField("Площадь (кв.м.)")
    house = models.ForeignKey(House, on_delete=models.CASCADE, verbose_name='Дом')
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, verbose_name="Секция", null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, verbose_name="Этаж", null=True, blank=True)
    owner = models.ForeignKey(Owner, on_delete=models.SET_NULL, verbose_name='Владелец', null=True, blank=True)
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, verbose_name="Тариф", null=True)

    def balance(self):
        if self.bankbook_set.first():
            return self.bankbook_set.first().balance()
        return '(нет счета)'

    def avg_expenses(self):
        sum_for_month = 0
        max_date = Receipt.objects.filter(flat_id=self.id).aggregate(Max('date__month')).get('date__month__max')
        min_date = Receipt.objects.filter(flat_id=self.id).aggregate(Min('date__month')).get('date__month__min')
        month_count = 0
        logger.info(str(min_date)+" "+str(max_date))
        if not all([max_date, min_date]):
            return '0.00'
        for i in range(min_date, max_date+1):
            receipts = Receipt.objects.filter(flat_id=self.id, date__month=i)
            month_count += 1
            for receipt in receipts:
                sum_for_month += receipt.get_price()
        try:
            return sum_for_month/month_count
        except ZeroDivisionError:
            return sum_for_month

    def __str__(self):
        return str(self.number)


class Receipt(models.Model):
    id = models.CharField("№", primary_key=True, max_length=15)
    date = models.DateField()
    date_from = models.DateField("Период с")
    date_to = models.DateField("Период по")
    flat = models.ForeignKey(Flat, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name="Квартира")
    is_checked = models.BooleanField("Проведена", default=True)
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True,
                               verbose_name='Тариф')

    class Status(models.TextChoices):
        paid = 'оплачена', _('оплачена')
        part = 'частично оплачена', _('частично оплачена')
        unpaid = 'не оплачена', _('не оплачена')
        __empty__ = _('')

    status = models.CharField("Статус", choices=Status.choices, max_length=20)
    services = models.ManyToManyField(Service, through='ReceiptService')

    def get_price(self):
        return self.receiptservice_set.all().aggregate(Sum('price')).get('price__sum', 0.00)


class ReceiptService(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.RESTRICT)
    amount = models.FloatField("Расход")
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)
    price_unit = models.FloatField("Цеа за 1 ед., грн.")
    price = models.FloatField("Стоимость, грн.")


class BankBook(models.Model):
    id = models.CharField('№', primary_key=True, max_length=15)
    flat = models.ForeignKey(Flat, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Квартира')

    class Status(models.TextChoices):
        active = 'Активен', _('Активен')
        disabled = 'Неактивен', _('Неактивен')
        __empty__ = _('')

    status = models.CharField("Статус", choices=Status.choices, max_length=20)

    def __str__(self):
        return self.id

    def balance(self):
        incomes = self.cashbox_set.filter(type='приход').aggregate(Sum('amount_of_money'))\
            .get('amount_of_money__sum', 0.00)
        receipts = sum([receipt.get_price() for receipt in self.flat.receipt_set.all()])
        logger.info(incomes)
        if incomes:
            return float(incomes)-receipts
        if receipts:
            return 0.00-receipts
        else:
            return 0.00