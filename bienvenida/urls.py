from django.urls import path
from . import views

urlspatterns = [
    path('inicio/', views.inicio, name='inicio')
]