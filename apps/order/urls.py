from django.urls import path, re_path
from django.conf.urls import url
from apps.order.views import OrderPlaceView, OrderCommitView

urlpatterns = [
    re_path(r'^place$', OrderPlaceView.as_view(), name='place'),  # 订单结算
    re_path(r'^commit$', OrderCommitView.as_view(), name='commit')  # 订单提交后台处理
]
