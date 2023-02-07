from django.core.management.base import BaseCommand

from admin_app.models import Role


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not Role.objects.all():
            roles = ['Директор', 'Управляющий', 'Бухгалтер', 'Электрик', 'Сантехник']
            for role in roles:
                _role = Role.objects.create(name=role)
                _role.save()
                print(role + ' created')