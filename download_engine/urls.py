from django.contrib import admin
from django.urls import path
from .views import downloader


urlpatterns = [
    path('course/<slug:course_title>/', downloader, name='downloader'),
]