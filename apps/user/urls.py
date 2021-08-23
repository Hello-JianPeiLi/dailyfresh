from django.urls import path
from django.conf.urls import url
from apps.user.views import RegisterView, ActiveView, LoginView, IndexView, OrderView

from django.urls import re_path
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # 注册
    re_path('active/(?P<token>.*)/', ActiveView.as_view(), name='active'),  # 激活
    path('login/', LoginView.as_view(), name='login'),  # 登录
    path('index/', IndexView.as_view(), name='index'),  # 登录
    path('order/', OrderView.as_view(), name='order'),  # 用户中心-订单
    path('index/', IndexView.as_view(), name='index'),  # 用户中心-订单
]
