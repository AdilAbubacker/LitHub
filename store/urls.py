from django.conf.urls.static import static
from django.urls import path
from core import settings
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('product_list/<str:category>/<str:slug>', views.product_list, name='product_list'),
    path('product_list/<str:category>/<str:slug>/<str:sort>', views.product_list, name='product_list'),
    path('product_details/<str:variant_slug>', views.product_details, name='product_details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)