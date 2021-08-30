from django.urls import path, re_path
from django.conf.urls import url
from apps.goods import views
from apps.goods.views import IndexView, DetailView

urlpatterns = [
    path('index/', IndexView.as_view(), name='index'),  # 首页
    re_path('goods/(?P<goods_id>\d+)', DetailView.as_view(), name='detail'),  # 根据goods_id查看详情页

]
