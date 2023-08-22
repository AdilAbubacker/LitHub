
from django.urls import path
from . import views

urlpatterns = [
    path('Signin', views.signin, name='signin'),
    path('signup', views.signup, name='signup'),
    path('signout', views.signout, name='signout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('otp_login', views.otp_login, name='otp_login'),
    path('generate_otp/<int:user_id>/<int:n>', views.generate_otp, name='generate_otp'),
]

