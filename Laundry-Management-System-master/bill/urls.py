from django.urls import path
from . import views

urlpatterns = [
   path('billing/<int:order_id>/', views.online_billing, name='online_billing'),
   path('initiate-payment/<int:bill_id>/', views.initiate_payment, name='initiate_payment'),
    path('bill/payment-callback/', views.payment_callback, name='payment_callback'),
    path('payment-status/', views.payment_status, name='payment_status'),
]

