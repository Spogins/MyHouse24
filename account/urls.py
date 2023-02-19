from django.urls import path

from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('login_owner/', LoginOwnerView.as_view(), name='login_owner'),
    path('logout/', logout_user, name='logout'),
    path('get_user_role', get_user_role, name='get_user_role'),
]