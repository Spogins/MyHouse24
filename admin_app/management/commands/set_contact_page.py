from django.core.management.base import BaseCommand

from admin_app.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not ContactPage.objects.all():
            seo = SeoText.objects.create()
            seo.save()
            form = ContactPage.objects.create()
            form.seo = seo
            form.save()
            print('ContactPage created')