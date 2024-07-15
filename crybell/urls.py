from django.urls import path
from . import views

urlpatterns = [
    path('',views.login,name='login'),
    path('signup.html', views.signup, name='signup'),
    path('login.html', views.login, name='login'),
    path('home.html', views.home, name='home'),
    path('forgot.html', views.forgot, name='forgot'),
    path('result',views.result,name='result'),
    path('upload_audio', views.upload_audio, name='upload_audio'),
    ]
