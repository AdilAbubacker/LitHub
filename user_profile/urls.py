from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_profile, name='user_profile'),
    path('address_management', views.address_management, name='address_management'),
    path('set_as_default/<int:address_id>', views.set_as_default, name='set_as_default'),
    path('delete_address/<int:address_id>', views.delete_address, name='delete_address'),
    path('add_address', views.add_address, name='add_address'),
    path('my_orders', views.my_orders, name='my_orders'),
    path('myorder_detail/<int:order_id>', views.myorder_detail, name='myorder_detail'),
    path('my_wishlist', views.my_wishlist, name='my_wishlist'),

]

