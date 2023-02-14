from django.core.management.base import BaseCommand

from admin_app.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not Info.objects.all():
            seo = SeoText.objects.create()
            seo.save()
            form = Info.objects.create()
            form.seo = seo
            form.save()
            print('Info created')
