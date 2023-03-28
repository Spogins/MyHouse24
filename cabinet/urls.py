from django.urls import path

from .views import *

urlpatterns = [
    path('index', index, name='index'),
    path('summary/<int:pk>', Summary.as_view(), name='summary'),
    path('receipt_list_cabinet', ReceiptList.as_view(), name='receipt_list_cabinet'),
    path('detail_receipt/<str:pk>', ReceiptDetail.as_view(), name='detail_receipt'),
    path('detail_flatservice/<int:pk>', FlatServiceDetail.as_view(), name='detail_flatservice'),
    path('receipt_pdf/<str:receipt_id>', render_pdf_view, name='receipt_pdf'),
    path('message_list/', MessageList.as_view(), name='message_list'),
    path('detail_message/<int:pk>', MessageDetail.as_view(), name='detail_message'),
    path('delete_messages', delete_message, name='delete_messages'),
    path('master_request_list', MasterRequestList.as_view(), name='master_request_list'),
    path('create_master_request', MasterRequestCreate.as_view(), name='create_master_request'),
    path('delete_master_request/<int:pk>', delete_master_request, name='delete_master_request'),
    path('owner_profile', OwnerProfile.as_view(), name='owner_profile'),
    path('update_owner/<int:pk>', UpdateOwner.as_view(), name='update_owner'),
]