from django.contrib import admin
from django.urls import path
from .views import downloader


urlpatterns = [
    path('<slug:slug>', downloader, name='downloader'),
]
