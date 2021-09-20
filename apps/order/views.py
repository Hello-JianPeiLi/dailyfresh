from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import reverse, redirect
from django_redis import get_redis_connection
from apps.goods.models import GoodsSKU
from apps.user.models import Address
from django.http import JsonResponse
from apps.order.models import OrderInfo, OrderGoods
from datetime import datetime


# Create your views here.
class OrderPlaceView(View):
    """订单结算页面"""

    def post(self, request):
        user = request.user
        sku_ids = request.POST.getlist('sku_ids')

        # 没有添加商品
        if not sku_ids:
            # 跳转到购物车页面
            return redirect(reverse('cart:show'))

        conn = get_redis_connection('default')
        cart_key = 'cart_%s' % user.id
        skus = []
        total_count = 0
        total_price = 0
        # 遍历sku_ids获取商品信息
        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            # 获取用户购买的数量
            count = conn.hget(cart_key, sku_id)
            # 计算小计
            amount = sku.price * int(count)
            # 动态复制给sku
            sku.amount = amount
            sku.count = int(count)
            skus.append(sku)
            total_count += int(count)
            total_price += amount
        # 运费
        transit_price = 10
        # 实付款
        total_pay = total_price + transit_price
        # 获取用户收货地址
        addrs = Address.objects.filter(user=user)
        sku_ids = ','.join(sku_ids)
        # 组织上下文
        context = {
            'skus': skus,
            'total_count': total_count,
            'total_price': total_price,
            'transit_price': transit_price,
            'total_pay': total_pay,
            'addrs': addrs,
            'sku_ids': sku_ids
        }

        return render(request, 'place_order.html', context)


class OrderCommitView(View):
    """订单提交处理"""

    def post(self, request):
        # 判断用户是否登录
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'code': 403, 'msg': '请先登录'})
            # 接收数据
        addr_id = request.POST.get('addr_id')
        sku_ids = request.POST.get('sku_ids')
        pay_method = request.POST.get('pay_method')

        # 校验数据完整性
        if not all([addr_id, sku_ids, pay_method]):
            return JsonResponse({'code': 409, 'msg': '参数缺失'})

        # 检查参数值
        if pay_method not in OrderInfo.PAY_METHOD.keys():
            return JsonResponse({'code': 101, 'msg': '不存在该支付方式'})

        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            return JsonResponse({'code': 1001, 'msg': '地址不存在'})

        # TODO: 创建订单核心业务
        # 生成订单号
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)
        # 运费
        transit_price = 10

        # 总数目和总金额
        total_count = 0
        total_price = 0
        # TODO: 向df_order_info中插入数据
        order = OrderInfo.objects.create(order_id=order_id,
                                         user=user,
                                         addr=addr,
                                         pay_method=pay_method,
                                         total_count=total_count,
                                         total_price=total_price,
                                         transit_price=transit_price,
                                         )

        # TODO: 用户订单中有几个商品就向df_order_goods中插入几条数据
        conn = get_redis_connection('default')
        cart_key = 'cart_%s' % user.id

        sku_ids = sku_ids.split(',')
        for sku_id in sku_ids:
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except GoodsSKU.DoesNotExist:
                return JsonResponse({'code': 309, 'msg': '商品不存在'})

            # 从redis中获取商品的数量
            count = conn.hget(cart_key, sku_id)

            # TODO: 向df_order_goods中添加一条数据
            OrderGoods.objects.create(order=order,
                                      sku=sku,
                                      count=count,
                                      price=sku.price)
            # TODO: 更新商品库存和销量
            sku.stock -= int(count)
            sku.sales += int(count)
            sku.save()

            # TODO:累加计算订单商品总数量和总价格
            amount = sku.price * int(count)
            total_price += amount
            total_count += int(count)

        # TODO: 更新订单信息表中的商品数量和总价格
        order.total_price = total_price
        order.total_count = total_count
        order.save()

        # TODO: 清除用户的的购物车信息
        conn.hdel(cart_key, *sku_ids)

        return JsonResponse({'code': 200, 'msg': '结算成功'})
