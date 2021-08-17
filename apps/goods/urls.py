from django.urls import path
from django.conf.urls import url
from apps.goods import views

urlpatterns = [
    path('index', views.index, name='index')
]
