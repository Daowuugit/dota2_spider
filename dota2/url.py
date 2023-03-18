from django.urls import path
from . import views


app_name = 'dota2'
urlpatterns = [
    path('', views.index, name='index'),
    path('patch/', views.patch, name='patch')
]
