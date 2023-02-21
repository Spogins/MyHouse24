from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Owner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    patronymic = models.CharField('Отчество', max_length=30)
    image = models.ImageField('Сменить изображение', upload_to='owners/', null=True, blank=True)
    birthday = models.DateField('Дата Рождения', null=True)
    info = models.TextField('О владельце (заметки)')
    phone = models.CharField('Телефон', max_length=15)
    viber = models.CharField('Viber', max_length=15)
    identify = models.DecimalField("ID", max_digits=6, decimal_places=0, unique=True, null=True)

    class Status(models.TextChoices):
        active = 'Активен', _('Активен')
        new = 'Новый', _('Новый')
        disabled = 'Отключен', _('Отключен')

    status = models.CharField("Статус", choices=Status.choices, max_length=20, default='Новый')

    @property
    def fullnamep(self):
        return f"{self.user.last_name} {self.user.first_name} {self.patronymic}"

    def fullname(self):
        return f"{self.user.last_name} {self.user.first_name} {self.patronymic}"

    def houses_str(self):
        flats = self.flat_set.all().distinct('house_id')
        houses = []
        for flat in flats:
            houses.append('<a href="' + reverse('detail_house', args=[flat.house.pk]) + '">' +
                          flat.house.name + '</a>')
        answer = '<br>'.join(houses)
        return mark_safe(answer)

    def flats_str(self):
        flats = self.flat_set.all()
        answer = []
        for flat in flats:
            answer.append('<a href="">№' + str(flat.number) + ' ' + flat.house.name + '</a>')
        return mark_safe('<br>'.join(answer))

    def __str__(self):
        return self.fullname()

    def has_debt(self):
        flats = self.flat_set.all()
        for flat in flats:
            if isinstance(flat.balance(), float) and flat.balance() < 0:
                return True
            else:
                return False


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField("Телефон", max_length=15, null=True, blank=True)

    class Role(models.TextChoices):
        director = 'Директор', _('Директор')
        manager = 'Управляющий', _('Управляющий')
        accountant = 'Бухгалтер', _('Бухгалтер')
        electrician = 'Электрик', _('Электрик')
        plumber = 'Сантехник', _('Сантехник')

    class Status(models.TextChoices):
        active = 'Активен', _('Активен')
        new = 'Новый', _('Новый')
        disabled = 'Отключен', _('Отключен')

    role = models.CharField("Роль", choices=Role.choices, max_length=20, default='Директор')
    status = models.CharField("Статус", choices=Status.choices, max_length=20, default='Новый')

    def __str__(self):
        return f'{self.role} - {self.user.first_name} {self.user.last_name}'







