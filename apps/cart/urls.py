from django.urls import path, re_path
from django.conf.urls import url
from .views import CartAddView, CartInfoView, CartUpdateView, CartDeleteView

urlpatterns = [
    path('add/', CartAddView.as_view(), name='add'),  # 购物车添加
    re_path(r'^$', CartInfoView.as_view(), name='show'),  # 购物车显示
    re_path(r'^update$', CartUpdateView.as_view(), name='update'),  # 购物车更新
    re_path(r'^delete', CartDeleteView.as_view(), name='delete')  # 删除购物车商品
]
