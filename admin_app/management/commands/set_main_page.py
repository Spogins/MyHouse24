from django.core.management.base import BaseCommand
from psycopg2.sql import NULL

from admin_app.models import *


class Command(BaseCommand):
    def handle(self, null=None, *args, **options):
        if not MainPage.objects.all():
            for x in range(3):
                slide = Slide.objects.create(image=None)
                slide.save()
                print(f'{x} Slide Done')
            for q in range(6):
                near_block = NearBlock.objects.create(image=None)
                near_block.save()
                print(f'{q} NearBlock Done')
            full_form = MainPage.objects.create()
            seo = SeoText.objects.create()
            seo.save()
            full_form.seo = seo
            full_form.save()
            print('MainPage Done')