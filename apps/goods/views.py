from django.shortcuts import render
from django.views.generic import View
from apps.goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner, GoodsSKU
from apps.order.models import OrderGoods
from django_redis import get_redis_connection
from django.shortcuts import redirect, reverse
from django.core.paginator import Paginator


# Create your views here.

# class Test(object):
#     def __init__(self):
#         self.name = 'abc'
#
# t = Test()
# t.age = 10
# print(t.age)


# http://127.0.0.1:8000/index
class IndexView(View):
    """首页"""

    def get(self, request):
        """显示首页"""
        # 获取商品的种类信息
        types = GoodsType.objects.all()

        # 首页轮播图展示
        goods_banners = IndexGoodsBanner.objects.all().order_by('index')

        # 获取首页促销详情
        promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

        # 获取首页分类商品展示信息
        for type in types:
            # 获取type种类首页分类商品的图片展示信息
            image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
            # 获取type种类首页分类商品的文字展示信息
            title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

            # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
            type.image_banners = image_banners
            type.title_banners = title_banners

        # 获取用户购物车中商品数量
        cart_count = 0
        user = request.user
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # 上下文
        context = {
            'types': types,
            'goods_banners': goods_banners,
            'promotion_banners': promotion_banners,
            'cart_count': cart_count
        }

        # 使用模板
        return render(request, 'index.html', context)


# /goods/goods_id
class DetailView(View):
    """商品详情页"""

    def get(self, request, goods_id):
        """显示详情页"""
        # 获取商品的种类信息
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return redirect(reverse('goods:index'))

        print(sku.goods)
        # 获取商品分类信息
        types = GoodsType.objects.all()

        # 获取商品评论信息
        sku_comment = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        # 获取新品推荐
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')

        #
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)

        # 获取购物车数量
        cart_count = 0
        user = request.user
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)
            # 用户历史记录
            conn = get_redis_connection('default')
            history_key = 'history_%d' % user.id
            # 移除列表中的goods_id
            conn.lrem(history_key, 0, goods_id)
            # 把goods_id插入到列表的左侧
            conn.lpush(history_key, goods_id)
            conn.ltrim(history_key, 0, 4)

        # 组织上下文模板
        context = {
            'sku': sku,
            'types': types,
            'new_skus': new_skus,
            'cart_count': cart_count,
            'sku_comment': sku_comment,
            'same_spu_skus': same_spu_skus
        }
        return render(request, 'detail.html', context)


# /list/1/2?sort=default
class ListView(View):
    """列表展示"""

    def get(self, request, type_id, page):
        try:
            # 查询种类
            type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            # 种类不存在
            return redirect(reverse('goods:index'))

        # 获取商品的分类信息
        types = GoodsType.objects.all()

        # 根据分类查询所有商品
        # 根据排序显示商品
        sort = request.GET.get('sort')
        if sort == 'price':
            # 根据价格降序
            skus = GoodsSKU.objects.filter(type=type).order_by('-price')
        elif sort == 'sales':
            # 根据销售量降序
            skus = GoodsSKU.objects.filter(type=type).order_by('-sales')
        else:
            # 根据商品id降序
            skus = GoodsSKU.objects.filter(type=type).order_by('-id')

        paginator = Paginator(skus, 1)
        # 获取页面
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1
        # 获取第page页的实例对象
        skus_page = paginator.page(page)

        # 获取新品推荐
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')

        # 购物车
        cart_count = 0
        user = request.user
        if user.is_authenticated:
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # 模板上下文
        context = {
            "types": types,
            'type': type,
            "skus_page": skus_page,
            "new_sku": new_skus,
            "cart_count": cart_count
        }
        return render(request, 'list.html', context)
