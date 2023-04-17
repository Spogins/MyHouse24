from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from account.models import Profile


class Command(BaseCommand):
    def handle(self, *args, **options):
        admin = User.objects.create()
        admin.first_name = 'admin'
        admin.last_name = 'admin'
        admin.email = 'admin@admin.com'
        admin.username = 'admin@admin.com'
        admin.is_superuser = True
        admin.is_stuff = True
        admin.set_password('523164')
        admin.save()
        profile = Profile.objects.create(
            user_id=admin.id,
            phone='(835)-555-44-69',
            role='Директор',
            status='Активен'
        )
        profile.save()
        print("Супер-админ Директор: настроен")
