from django.contrib import admin
from apps.goods.models import GoodsType
from apps.goods.models import IndexTypeGoodsBanner, GoodsSKU, Goods

# Register your models here.

admin.site.register(GoodsType)
admin.site.register(IndexTypeGoodsBanner)
admin.site.register(GoodsSKU)
admin.site.register(Goods)
