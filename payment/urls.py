from django.urls import path
from . import views

urlpatterns = [
    # urls.py
    # path('payment/<slug:slug>/', views.payment_by_slug_view, name='payment_page'),
     # GET form for selecting subject & payment
    path('create-order/', views.create_order, name='create_razorpay_order'),
    path('verify-payment/', views.verify_payment, name='verify_razorpay_payment'),
    path('history/', views.transaction_history, name='transaction_history'),
]



