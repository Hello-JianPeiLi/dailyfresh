from django.contrib import admin
from apps.goods.models import GoodsType
from apps.goods.models import IndexTypeGoodsBanner, GoodsSKU, Goods,IndexGoodsBanner,IndexPromotionBanner

# Register your models here.

admin.site.register(GoodsType)
admin.site.register(IndexTypeGoodsBanner)
admin.site.register(GoodsSKU)
admin.site.register(Goods)
admin.site.register(IndexGoodsBanner)
admin.site.register(IndexPromotionBanner)
