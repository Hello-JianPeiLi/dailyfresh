import os
from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import reverse, redirect
from django_redis import get_redis_connection
from apps.goods.models import GoodsSKU
from apps.user.models import Address
from django.http import JsonResponse
from apps.order.models import OrderInfo, OrderGoods
from datetime import datetime
from django.db import transaction
from alipay import AliPay, ISVAliPay
from dailyfresh import settings


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


# class OrderCommitView(View):
#     """订单提交处理 悲观锁"""
#
#     @transaction.atomic
#     def post(self, request):
#         # 判断用户是否登录
#         user = request.user
#         if not user.is_authenticated:
#             return JsonResponse({'code': 403, 'msg': '请先登录'})
#             # 接收数据
#         addr_id = request.POST.get('addr_id')
#         sku_ids = request.POST.get('sku_ids')
#         pay_method = request.POST.get('pay_method')
#
#         # 校验数据完整性
#         if not all([addr_id, sku_ids, pay_method]):
#             return JsonResponse({'code': 409, 'msg': '参数缺失'})
#
#         # 检查参数值
#         if pay_method not in OrderInfo.PAY_METHOD.keys():
#             return JsonResponse({'code': 101, 'msg': '不存在该支付方式'})
#
#         try:
#             addr = Address.objects.get(id=addr_id)
#         except Address.DoesNotExist:
#             return JsonResponse({'code': 1001, 'msg': '地址不存在'})
#
#         # TODO: 创建订单核心业务
#         # 生成订单号
#         order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)
#         # 运费
#         transit_price = 10
#
#         # 总数目和总金额
#         total_count = 0
#         total_price = 0
#
#         save_id = transaction.savepoint()
#         # TODO: 向df_order_info中插入数据
#         try:
#             order = OrderInfo.objects.create(order_id=order_id,
#                                              user=user,
#                                              addr=addr,
#                                              pay_method=pay_method,
#                                              total_count=total_count,
#                                              total_price=total_price,
#                                              transit_price=transit_price,
#                                              )
#
#             # TODO: 用户订单中有几个商品就向df_order_goods中插入几条数据
#             conn = get_redis_connection('default')
#             cart_key = 'cart_%s' % user.id
#
#             sku_ids = sku_ids.split(',')
#             for sku_id in sku_ids:
#
#                 try:
#                     # 悲观锁
#                     sku = GoodsSKU.objects.select_for_update().get(id=sku_id)
#                 except GoodsSKU.DoesNotExist:
#                     transaction.savepoint_rollback(save_id)
#                     return JsonResponse({'code': 309, 'msg': '商品不存在'})
#
#                 print('user_id:%s' % user.id, 'stock:%s' % sku.stock)
#                 import time
#                 time.sleep(10)
#                 # 从redis中获取商品的数量
#                 count = conn.hget(cart_key, sku_id)
#
#                 # 判断商品库存
#                 if int(count) > sku.stock:
#                     transaction.savepoint_rollback(save_id)
#                     return JsonResponse({'code': 308, 'msg': '商品库存不足'})
#
#                 # TODO: 向df_order_goods中添加一条数据
#                 OrderGoods.objects.create(order=order,
#                                           sku=sku,
#                                           count=count,
#                                           price=sku.price)
#                 # TODO: 更新商品库存和销量
#                 sku.stock -= int(count)
#                 sku.sales += int(count)
#                 sku.save()
#
#                 # TODO:累加计算订单商品总数量和总价格
#                 amount = sku.price * int(count)
#                 total_price += amount
#                 total_count += int(count)
#
#             # TODO: 更新订单信息表中的商品数量和总价格
#             order.total_price = total_price
#             order.total_count = total_count
#             order.save()
#         except:
#             return JsonResponse({'code': 000, 'msg': '数据出错'})
#
#         # TODO: 清除用户的的购物车信息
#         conn.hdel(cart_key, *sku_ids)
#
#         return JsonResponse({'code': 200, 'msg': '结算成功'})

# /order/commit
class OrderCommitView(View):
    """订单提交处理 乐观锁"""

    @transaction.atomic
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

        save_id = transaction.savepoint()
        # TODO: 向df_order_info中插入数据
        try:
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
                for i in range(3):
                    try:
                        # 悲观锁
                        sku = GoodsSKU.objects.get(id=sku_id)
                    except GoodsSKU.DoesNotExist:
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'code': 309, 'msg': '商品不存在'})
                    print('user_id:%s，time:%s,stock:%s' % (user.id, i, sku.stock))

                    # 从redis中获取商品的数量
                    count = conn.hget(cart_key, sku_id)

                    # 判断商品库存
                    if int(count) > sku.stock:
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'code': 308, 'msg': '商品库存不足'})

                    origin_stock = sku.stock
                    new_stock = origin_stock - int(count)
                    new_sales = origin_stock + int(count)

                    res = GoodsSKU.objects.filter(id=sku.id, stock=origin_stock).update(stock=new_stock,
                                                                                        sales=new_sales)
                    if res == 0:
                        if i == 2:
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'code': 924, 'msg': '提交失败'})
                        continue
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
                    # 如果一次就成功跳出for循环f
                    break
            # TODO: 更新订单信息表中的商品数量和总价格
            order.total_price = total_price
            order.total_count = total_count
            order.save()
        except:
            return JsonResponse({'code': 000, 'msg': '数据出错'})

        # TODO: 清除用户的的购物车信息
        conn.hdel(cart_key, *sku_ids)

        return JsonResponse({'code': 200, 'msg': '结算成功'})


class OrderPayView(View):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'code': 929, 'msg': '请登录'})

        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'code': 23, 'msg': '参数缺失'})

        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code': 123, 'msg': '订单不存在'})

        # 业务处理使用Python sdk调用支付宝支付接口
        # 初始化
        app_private_key_path = os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem')
        app_public_key_path = os.path.join(settings.BASE_DIR, 'apps/order/app_public_key.pem')
        app_private_key_string = open(app_private_key_path, 'r').read()
        app_public_key_string = open(app_public_key_path, 'r').read()
        alipay = AliPay(
            appid='2021000118621468',
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=app_public_key_string,
            sign_type='RSA2',
            debug=True
        )

        # 调用支付接口
        # 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        total_pay = order.total_price + order.transit_price
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单id
            total_amount=str(total_pay),  # 支付总金额
            subject='我是主角买单---%s' % order_id,
            return_url=None,
            notify_url=None,  # 可选，不填则使用默认的notify url
        )

        # 返回应答
        pay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string
        return JsonResponse({'code': 125, 'pay_url': pay_url})
