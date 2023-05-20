from django.urls import path
from . import views
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from .views import clear_templates
from django.urls import re_path

urlpatterns = [
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('', views.templates_view, name='home'),
    path('templates/<int:video_number>/', views.templates_view, name='template_detail'),
    path('accounts/login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('clear_templates/', clear_templates, name='clear_templates'),
    path('template_detail/<int:video_number>/', views.template_detail, name='template_detail'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('capture_frame/<int:video_number>/', views.capture_last_frame, name='capture_frame'),
]
