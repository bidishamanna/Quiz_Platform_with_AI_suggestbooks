from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('', views.cart_detail, name='cart'),  # No extra "cart/" prefix here
    path('update/<int:item_id>/', views.update_cart, name='update_cart'),
    path("checkout/", views.checkout, name="checkout"), 
]
