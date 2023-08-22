from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_summary, name='cart_summary'),
    path('add_to_cart/<int:variant_id>/<int:source>', views.add_to_cart, name='add_to_cart'),
    path('add_to_cart/<int:variant_id>', views.add_to_cart, name='add_to_cart'),
    path('update_quantity/<int:cart_item_id>/<int:num>', views.update_quantity, name='update_quantity'),
    path('remove_cart_item/<int:cart_item_id>', views.remove_cart_item, name='remove_cart_item'),
    path('wishlist', views.wishlist_summary, name='wishlist_summary'),
    path('add_to_wishlist/<int:variant_id>', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:wishlist_item_id>', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist_to_cart/<int:wishlist_item_id>', views.wishlist_to_cart, name='wishlist_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
]

