from django.urls import path
from . import views

urlpatterns = [
    # path('orders/', views.orders, name='orders'),
    path('order_placed', views.order_placed, name='order_placed'),
    path('initiate_payment/', views.initiate_payment, name='initiate_payment'),
    path('online_payment_order/', views.online_payment_order, name='online_payment_order'),
    path('order_successful', views.order_successful, name='order_successful'),
    path('order_pdf/<int:order_id>', views.order_pdf, name='order_pdf'),
    path('cancel_order/<int:order_id>', views.cancel_order, name='cancel_order'),
    path('request_return/<int:order_id>', views.request_return, name='request_return'),
]
