from django.urls import path
from django.conf.urls import url
from apps.user.views import (RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, LoginOutView,
                             UserAddressView)

from django.urls import re_path
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # 注册
    re_path('active/(?P<token>.*)/', ActiveView.as_view(), name='active'),  # 激活
    path('login/', LoginView.as_view(), name='login'),  # 登录
    path('logout/', LoginOutView.as_view(), name='logout'),  # 登出
    path('order/', UserOrderView.as_view(), name='order'),  # 用户中心-订单
    path('', UserInfoView.as_view(), name='index'),  # 用户中心-信息
    path('address/', UserAddressView.as_view(), name='address'),  # 用户中心-地址
]
