from django.urls import path
from django.contrib.auth import views as auth_views
from .views import csv_upload, download_excel
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('upload/', views.csv_upload, name='csv_upload'),
    path('download_excel/', download_excel, name='download_excel'),
]
