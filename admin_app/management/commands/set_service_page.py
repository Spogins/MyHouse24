from django.core.management.base import BaseCommand

from admin_app.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not ServicePage.objects.all():
            seo = SeoText.objects.create()
            full_form = ServicePage.objects.create()
            full_form.seo = seo
            full_form.save()
            print('ServicePage created')