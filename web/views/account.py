import re
import random
from django.http import JsonResponse
from web import models
from utils.encrypt import md5
from django.shortcuts import render, redirect
from .forms import LoginForm, SmsLoginForm


def login(request):
    if request.method == 'GET':
        # GET请求：实例化一个干干净净的空表单
        form = LoginForm()
        return render(request, "login.html", {"form": form})

    # POST请求：将前端传来的数据绑定到表单
    form = LoginForm(data=request.POST)

    # 这一步会自动进行非空校验，如果不通过，form里面就会携带错误信息
    if form.is_valid():# 验证通过后，cleaned_data 才可用
        # 清洗后的安全数据
        # ✅ 这里！form.cleaned_data 包含验证通过的数据
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        role = form.cleaned_data.get('role')

        password_md5 = md5(password)  # 你的加密逻辑

        # 数据库校验
        query_params = {'active': 1, 'username': username, 'password': password_md5}
        if role == "1":
            user_object = models.Administrator.objects.filter(**query_params).first()
        else:
            user_object = models.Customer.objects.filter(**query_params).first()

        # 校验成功
        if user_object:
            mapping = {"1": "ADMIN", "2": "CUSTOMER"}
            request.session['user_info'] = {
                'role': mapping[role],
                'name': user_object.username,
                'id': user_object.id
            }
            return redirect("/level/list/")

        # 校验失败：查无此人或密码错误。通过 add_error 附加一个全局错误
        form.add_error(None, "用户名或密码错误")

    # 如果代码走到这里（验证没通过，或数据库查不到），直接把带有数据的 form 传回前端
    # Django Form 会自动帮你完成刚才讨论的“数据回显”
    return render(request, "login.html", {"form": form})


def sms_login(request):
    """ 处理短信登录页面展示 & AJAX 登录请求 """
    # 1. 页面渲染 (GET 请求)
    if request.method == 'GET':
        # GET请求：实例化一个干干净净的空表单
        form = SmsLoginForm()
        return render(request, "sms_login.html", {"form": form})
    # 2. 登录校验 (POST 请求，来自 AJAX)
    # 接收 AJAX 传过来的所有表单数据进行绑定
    form = SmsLoginForm(data=request.POST)
    # form基础校验
    if form.is_valid():
        mobile = form.cleaned_data.get('mobile')
        code = form.cleaned_data.get('code')
        role = form.cleaned_data.get('role')

        # 去 Session 里找刚刚 `sms_send` 存进去的正确答案
        session_code = request.session.get('sms_code')
        session_mobile = request.session.get('sms_mobile')
        if not session_code:
            return JsonResponse({'status': False, 'error': '验证码已过期，请重新获取'})
        if mobile != session_mobile or code != session_code:
            return JsonResponse({'status': False,  'error':'验证码错误或手机号不匹配'})

        # 数据库校验
        query_params = {'active': 1, 'mobile': mobile}
        if role == "1":
            user_object = models.Administrator.objects.filter(**query_params).first()
        else:
            user_object = models.Customer.objects.filter(**query_params).first()

        if not user_object:
            return JsonResponse({'status': False, 'error': '该手机号未注册或角色选择错误'})

        # 登录成功
        # 把用过的验证码作废，防止他按浏览器返回键重复利用
        del request.session['sms_code']
        del request.session['sms_mobile']

        # 写入用户信息到 Session
        mapping = {"1": "ADMIN", "2": "CUSTOMER"}
        request.session['user_info'] = {
            'role': mapping[role],
            'name': user_object.username,
            'id': user_object.id
        }
        # 页面跳转了
        return JsonResponse({'status': True, 'redirect_url': '/level/list/'})
    # 4. Form 基础校验失败的兜底
    # ==========================================
    # 如果第一关 Form 校验就没过（比如手机号格式瞎填），提取第一条报错信息返回
    error_msg = list(form.errors.values())[0][0]
    return JsonResponse({'status': False, 'error': error_msg})


def sms_send(request):
    # 1. 接收前端 AJAX 传过来的手机号 (这里我们用 GET 请求比较简单)
    mobile = request.GET.get('mobile')
    # 2. 基础校验
    if not mobile:
        return JsonResponse({'status': False, 'error': '请先输入手机号'})
    # 用正则表达式检查是不是 11 位中国手机号
    if not re.match(r'^1[3-9]\d{9}$', mobile):
        return JsonResponse({'status': False, 'error': '手机号格式不正确'})

    # 3. 生成 6 位随机验证码
    code = str(random.randint(100000, 999999))

    # 【模拟发送短信】实际开发中这里会调用阿里云、腾讯云的短信 API
    print(f"【系统提示】正在向手机号 {mobile} 发送短信验证码: {code}")

    # 4. 把验证码和手机号存进 Session 中，留给等下的 login 视图去校验比对！
    request.session['sms_code'] = code
    request.session['sms_mobile'] = mobile
    # 可以设置验证码过期时间，比如 60 秒 (可选)
    request.session.set_expiry(60)

    # 5. 告诉前端：发送成功！
    return JsonResponse({'status': True, 'msg': '验证码发送成功'})
