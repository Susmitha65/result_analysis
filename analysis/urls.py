from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('upload/', views.csv_upload, name='csv_upload'),
]
