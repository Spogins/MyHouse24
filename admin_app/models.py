from django.db import models


# Create your models here.
class House(models.Model):
    pass


class SeoBlock(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    keywords = models.TextField()


class HomePage(models.Model):
    slide_1 = models.ImageField(upload_to='slides/', null=True, blank=True)
    slide_2 = models.ImageField(upload_to='slides/', null=True, blank=True)
    slide_3 = models.ImageField(upload_to='slides/', null=True, blank=True)


class Unit(models.Model):
    name = models.CharField(max_length=10)

    class Meta:
        unique_together = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=20)
    unit = models.ForeignKey(Unit, on_delete=models.RESTRICT, null=True, blank=True)
    show = models.BooleanField(default=False)

    class Meta:
        unique_together = ['name']

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







