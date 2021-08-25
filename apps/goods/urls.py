from django.urls import path
from django.conf.urls import url
from apps.goods import views
from apps.goods.views import IndexView

urlpatterns = [
    path('index/', IndexView.as_view(), name='index')
]
