from django.urls import path
from django.conf.urls import url
<<<<<<< HEAD
from apps.user.views import RegisterView, ActiveView, LoginView, IndexView
=======
from apps.user.views import RegisterView, ActiveView, LoginView, OrderView
>>>>>>> dfff577f6661e127f280946dc12688d11ba735d1
from django.urls import re_path
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),  # 注册
    re_path('active/(?P<token>.*)/', ActiveView.as_view(), name='active'),  # 激活
    path('login/', LoginView.as_view(), name='login'),  # 登录
<<<<<<< HEAD
    path('index/', IndexView.as_view(), name='index'),  # 登录
=======
    path('order/', OrderView.as_view(), name='order'),  # 用户中心-订单
>>>>>>> dfff577f6661e127f280946dc12688d11ba735d1
]
