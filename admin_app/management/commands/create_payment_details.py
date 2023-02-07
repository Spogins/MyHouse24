from django.core.management.base import BaseCommand

from admin_app.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not PaymentDetails.objects.all():
            pay_d = PaymentDetails.objects.create()
            pay_d.save()
            print('PaymentDetails created')