from django.urls import path
from django.conf.urls import url
from .views import CartAddView

urlpatterns = [
    path('add/', CartAddView.as_view(), name='add')  # 购物车添加
]
