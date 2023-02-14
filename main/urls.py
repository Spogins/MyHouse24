from django.urls import path

from .views import *

urlpatterns = [
    path('', MainPageView.as_view(), name='main_page'),
    path('about_us', AboutUsPage.as_view(), name='about_us_page'),
    path('services', ServicePage.as_view(), name='service_page'),
    path('contacts', ContactPage.as_view(), name='contact_page')

]