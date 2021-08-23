from django.shortcuts import render, redirect
from django.views.generic import View
from django.urls import reverse
from django.http import HttpResponse
import re
from apps.user.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from dailyfresh import settings
from django.core.mail import send_mail
from itsdangerous import SignatureExpired

from celery_tasks.email_task import send_register_active_email
from django.contrib.auth import authenticate, login
from utils.mixin import LoginRequireMixin


# from celery_tasks.email_task import send_register_active_email

# /user/register
class RegisterView(View):
    """注册页面"""

    def get(self, request):
        """获取注册页面"""
        return render(request, 'register.html')

    def post(self, request):
        """注册处理"""
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')

        # 进行数据校验
        if not all([username, password, email]):
            return render(request, 'register.html', {'error': '数据不完整'})

        # 邮箱校验
        if not re.match(r'[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'error': '邮箱格式不正确'})

        # 检测用户名是否重复
        try:
            user = User.objects.get(username=username, password=password)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名存在
            return render(request, 'register.html', {'error': '用户名已存在'})

        # 业务处理进行注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 生成激活连接
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info).decode('utf-8')

        # 发送邮件
        username = user.username
        # msg = '<h1>%s,欢迎注册，请点击下方连接激活</h1><a href="http://127.0.0.1:7890/user/active/%s">http://127.0.0.1:7890/user/active/%s</a>' % (
        #     user.username, token, token)
        # sender = '291075564@qq.com'
        # subject = 'django项目，注册激活'
        # send_mail(subject, msg, sender, ['root_pei@163.com'], html_message=msg, )
        # 将邮件放到broker去做
        # send_register_active_email.delay(username, token)

        # 注册完跳转到首页
        return redirect(reverse('goods:index'))


class ActiveView(View):
    """链接激活处理"""

    def get(self, request, token):
        # 点击激活链接后进来激活处理
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            # 反向解析跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return HttpResponse("激活链接已过期")


# /user/login
class LoginView(View):
    """登录页面"""

    def get(self, request):
        if 'username' in request.COOKIES:
            username = request.COOKIES['username']
        else:
            username = ''
        return render(request, 'login.html', {'username': username})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        if not all([username, password]):
            return render(request, 'login.html', {'error': '请填写账号或密码'})
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户密码正确
            # 是否激活
            if user.is_active:
                login(request, user)
                # 判断是否记住账号
                response = redirect(reverse('user:index'))
                remember = request.POST.get('remember')
                if remember == 'on':
                    response.set_cookie('username', username, max_age=60)
                else:
                    response.delete_cookie('username')
                return response
            else:
                return render(request, 'login.html', {'error': '用户未激活'})
        else:
            return render(request, 'login.html', {'error': '账号或密码错误'})


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')


class OrderView(LoginRequireMixin, View):
    def get(self, request):
        return render(request, 'user_center_order.html')
