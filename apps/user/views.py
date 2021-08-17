from django.shortcuts import render, redirect
from django.views.generic import View
from django.urls import reverse
from django.http import HttpResponse
import re
from apps.user.models import User


# Create your views here.

class RegisterView(View):
    # /user/register
    def get(self, request):
        """获取注册页面"""
        return render(request, 'register.html')

    # /user/register
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

        # 业务处理进行注册
        user = User.objects.create_user(username, password, email)

        # 注册完跳转到首页
        return redirect(reverse('goods:index'))
