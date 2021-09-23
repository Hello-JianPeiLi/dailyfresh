from django.urls import path, re_path
from django.conf.urls import url
from apps.order.views import OrderPlaceView, OrderCommitView, OrderPayView, CheckPayView

urlpatterns = [
    re_path(r'^place$', OrderPlaceView.as_view(), name='place'),  # 订单结算
    re_path(r'^commit$', OrderCommitView.as_view(), name='commit'),  # 订单提交后台处理
    re_path(r'^pay$', OrderPayView.as_view(), name='pay'),  # 支付处理
    re_path(r'^check$', CheckPayView.as_view(), name='check')  # 支付处理
]
