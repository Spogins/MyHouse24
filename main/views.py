from django.shortcuts import render
from django.views.generic import FormView

from admin_app.models import *


# Create your views here.

class MainPageView(FormView):
    template_name = 'main/pages/main_page.html'
    try:
        main_page = MainPage.objects.first()
        near = NearBlock.objects.all()
        contacts = ContactPage.objects.first()
        gallery = Slide.objects.all()
    except:
        main_page = None
        near = None
        contacts = None
        gallery = None

    def get_context_data(self, **kwargs):
        context = {
            'template_name': self.template_name,
            'main_page': self.main_page,
            'near': self.near,
            'contacts': self.contacts,
            'gallery': self.gallery
        }
        return context


class AboutUsPage(FormView):
    template_name = 'main/pages/about_us_page.html'
    try:
        page = Info.objects.all()[0]
        gallery_main = Gallery.objects.filter(additional=False)
        gallery_additional = Gallery.objects.filter(additional=True)
        documents = Document.objects.all()
    except:
        page = None
        gallery_main = None
        gallery_additional = None
        documents = None

    def get_context_data(self, **kwargs):
        context = {
            'page': self.page,
            'gallery_main': self.gallery_main,
            'gallery_additional': self.gallery_additional,
            'documents': self.documents,

        }
        return context


class ServicePage(FormView):
    template_name = 'main/pages/service_page.html'
    try:
        page = ServicePage.objects.all()[0]
        services = ServiceBlock.objects.all()
    except:
        page = None
        services = None

    def get_context_data(self, **kwargs):
        context = {
            'page': self.page,
            'services': self.services,
        }
        return context


class ContactPage(FormView):
    template_name = 'main/pages/contact_page.html'
    try:
        page = ContactPage.objects.first()
    except:
        page = None

    def get_context_data(self, **kwargs):
        context = {
            'page': self.page,
        }
        return context