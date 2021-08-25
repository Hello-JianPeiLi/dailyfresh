# -*- coding:utf-8 -*-
# Author: JianPei
# @Time : 2021/08/19 14:55
import django
from celery import Celery
from django.core.mail import send_mail
import os
import time

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


def generate_static_index_html():
    pass
