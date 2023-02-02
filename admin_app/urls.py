from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('services/', CreateService.as_view(), name='services'),
    path('delete_service', delete_service, name='delete_service'),
    path('delete_unit', delete_unit, name='delete_unit'),
    path('tariff_list/', TariffList.as_view(), name='tariff_list'),
    path('create_tariff/', CreateTariff.as_view(), name='create_tariff'),
    path('update_tariff/<int:pk>', UpdateTariff.as_view(), name='update_tariff'),
    path('tariff/<int:pk>', ShowTariff.as_view(), name='tariff'),
    path('get_unit_by_service', get_unit_by_service, name='get_unit_by_service'),
    path('tariff_list/delete_tariff/<int:tariff_id>', delete_tariff, name='delete_tariff'),
    path('delete_service_tariff', delete_service_tariff, name='delete_service_tariff'),
]