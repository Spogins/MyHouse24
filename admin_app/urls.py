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
    path('roles/', RoleList.as_view(), name='roles'),
    path('user_list/', UserList.as_view(), name='user_list'),
    path('create_user/', CreateUser.as_view(), name='create_user'),
    path('update_user/<int:pk>', UpdateUser.as_view(), name='update_user'),
    path('user_list/delete_user/<int:user_id>', delete_user, name='delete_user'),
    path('show_profile/<int:pk>', ShowProfile.as_view(), name='show_profile'),
    path('payment_details/', PaymentDetailsView.as_view(), name='payment_details'),
    path('payment_items/', PaymentItemList.as_view(), name='payment_items'),
    path('create_payment/', PaymentItemCreate.as_view(), name='create_payment'),
    path('update_payment/<int:pk>', PaymentItemUpdate.as_view(), name='update_payment'),
    path('payment_items/delete_payment/<int:payment_id>', delete_payment, name='delete_payment'),

]