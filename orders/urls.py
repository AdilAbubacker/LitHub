from django.urls import path
from . import views

urlpatterns = [
    # path('orders/', views.orders, name='orders'),
    path('order_placed', views.order_placed, name='order_placed'),
    path('initiate_payment/', views.initiate_payment, name='initiate_payment'),
    path('online_payment_order/', views.online_payment_order, name='online_payment_order'),
]
