# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/08/19 14:55
import django
from celery import Celery
from django.core.mail import send_mail
import os
from apps.goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner, IndexPromotionBanner
from django.template import loader, RequestContext
from dailyfresh import settings

# 为worker初始化环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
django.setup()

app = Celery('celery_tasks.email_task', broker='redis://172.16.126.198/2')


@app.task
def send_register_active_email(username, token):
    """发短信"""
    msg = '<h1>%s,欢迎注册，请点击下方连接激活</h1><a href="http://127.0.0.1:7890/user/active/%s">http://127.0.0.1:7890/user/active/%s</a>' % (
        username, token, token)
    sender = '291075564@qq.com'
    subject = 'django项目，注册激活'
    send_mail(subject, '', sender, ['root_pei@163.com'], html_message=msg, )


@app.task
def generate_static_index_html():
    # 获取商品的种类信息
    types = GoodsType.objects.all()

    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息
    for type in types:  # GoodsType
        # 获取type种类首页分类商品的图片展示信息  # display_type:1是图片 0是标题
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        # 获取type种类首页分类商品的文字展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
        type.image_banners = image_banners
        type.title_banners = title_banners

    # 组织模板上下文
    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners}

    # 使用模板
    # 1.加载模板文件
    temp = loader.get_template('static_index.html')
    # 2.定义模板上下文
    # context = RequestContext(request, context)
    # 3.模板渲染
    static_index_html = temp.render(context)
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)
