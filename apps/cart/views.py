from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from apps.goods.models import GoodsSKU
from django_redis import get_redis_connection
from django.shortcuts import redirect, reverse


# 添加商品到购物车
# 传递参数 商品id(sku_id) 商品数量(count)

# /cart/add
class CartAddView(View):
    """购物车记录添加"""

    def post(self, request):
        """购物车记录添加"""
        # 获取数据
        user = request.user
        print(user.id)
        if not user.is_authenticated:
            # 用户未登录
            return JsonResponse({'res': 5, 'msg': '请先登录'})
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 0, 'msg': '数据不完整'})

        # 校验添加的商品数量
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 1, 'msg': '数目出错'})

        # 检验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res': 2, 'msg': '商品不存在'})

        # 业务处理
        conn = get_redis_connection('default')
        cart_key = 'cart_%s' % user.id
        # 获取sku_id的值 hget cart_key
        # 如果sku_id在hash中不存在，则返回None
        cart_count = conn.hget(cart_key, sku_id)
        if cart_count:
            # 如果用户hash有记录则追加count
            count += int(cart_count)
        if count > sku.stock:
            return JsonResponse({'res': 4, 'msg': '商品库存不足'})
        conn.hset(cart_key, sku_id, count)

        total_count = conn.hlen(cart_key)
        # 返回应答
        return JsonResponse({'res': 3, 'total_count': total_count, 'msg': '添加成功'})
