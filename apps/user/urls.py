from django.urls import path
from django.conf.urls import url
from apps.user import views

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register')
]
