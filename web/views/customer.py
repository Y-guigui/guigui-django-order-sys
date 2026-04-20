import re
import random

from django.db import transaction
from django.http import JsonResponse
from web import models
from utils.encrypt import md5
from django.shortcuts import render, redirect
from .forms import CustomerForm, CustomerEditForm, ChargeModelForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def customer_list(request):
    # 获取前端传过来的搜索关键字 (默认是个空字符串)
    keyword = request.GET.get('q', '')
    query_dict = {'active': 1}
    # 如果用户输入了关键字，用户名模糊搜索条件
    if keyword:
        # __contains 就等价于 SQL 里面的 LIKE '%keyword%'
        query_dict['username__contains'] = keyword

    # 查数据库，并排序
    data_list = models.Customer.objects.filter(**query_dict).select_related('level', 'creator').order_by('id')
    # 实例化分类器paginator
    paginator = Paginator(data_list, 8)
    # 从 URL 提取用户想看的页码，默认看第 1 页
    page = request.GET.get('page',1)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # 如果用户输入的页码不是数字，就让他看第 1 页
        queryset = paginator.page(1)
    except EmptyPage:
        # 如果用户输入的页码太大了，就让他看最后一页
        queryset = paginator.page(paginator.num_pages)

    return render(request, 'customer_list.html', {
        'queryset': queryset,
        'keyword': keyword
    })


def customer_add(request):
    if request.method == 'GET':
        form = CustomerForm()
        return render(request, 'customer_add.html', {'form':form})

    # POST 请求，接收用户提交的数据进行绑定
    form = CustomerForm(data=request.POST)
    if form.is_valid():
        #ModelForm：验证通过后，直接调用save(),就会自动存入数据库
        instance = form.save(commit=False)
        admin_info = request.session.get("user_info")
        if admin_info:
            instance.creator_id = admin_info.get("id")
        instance.save()
        # 保存成功后跳转回列表页
        return redirect('customer_list')

    # 验证失败，带着错误信息返回原页面
    return render(request, 'customer_add.html', {'form':form})


def customer_edit(request, pk):
    instance = models.Customer.objects.filter(id=pk, active=1).first()
    if not instance:
        return redirect('customer_list')

    page = request.GET.get('page', '')
    q = request.GET.get('q', '')

    if request.method == 'GET':
        form = CustomerEditForm(instance=instance)
        return render(request, 'customer_edit.html', {'form':form})

    if request.method == 'POST':
        form = CustomerEditForm(data=request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(f'/customer/list/?page={page}&q={q}')

        return render(request, 'customer_edit.html', {'form':form})

def customer_delete(request, pk):
    """
    软删除客户 (Ajax 调用)
    """
    # 核心逻辑：不去查 exists，也不用 delete()
    # 直接找到这个 ID，把 active 字段更新为 0
    models.Customer.objects.filter(id=pk).update(active=0)

    # 返回成功的 JSON，前端的 SweetAlert 收到 True 就会弹出绿勾并刷新页面
    return JsonResponse({"status": True})


def customer_charge(request, pk):
    """
    某客户的交易记录列表
    """
    # 验证客户active=1
    customer_object = models.Customer.objects.filter(id=pk, active=1).first()
    if not customer_object:
        return redirect('customer_list')
    # 记录
    data_list = models.TransactionRecord.objects.filter(customer_id=pk, active=1).order_by('-id')

    paginator = Paginator(data_list, 8)
    page = request.GET.get('page', 1)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    return render(request, 'customer_charge.html', {
        'customer_object': customer_object,
        'queryset': queryset
    })

def customer_charge_add(request, pk):
    """
    新建交易记录（充值/扣款）
    :param request:
    :param pk:
    :return:
    """
    customer_object= models.Customer.objects.filter(id=pk, active=1).first()
    if not customer_object:
        return redirect('customer_list')
    if request.method == 'GET':
        form = ChargeModelForm()
        return render(request, 'customer_charge_add.html', {
            'form':form,
            'customer_object':customer_object
        })

    form = ChargeModelForm(data=request.POST)
    if form.is_valid():
        # 客户表
        amount = form.cleaned_data.get('amount')
        change_type = form.cleaned_data.get('change_type')

        if change_type == 2 and amount > customer_object.balance:
            form.add_error('amount', '账户余额不足,余额为{}，无法完成扣款！'.format(customer_object.balance))
            return render(request, 'customer_charge_add.html', {
                'form': form,
                'customer_object': customer_object
            })

        with transaction.atomic():
            # 补全字段，上面只是有'change_type'/'amount'/'memo'/'creator'
            instance = form.save(commit=False)
            instance.customer = customer_object
            instance.save()  # 存入交易记录表
            if change_type == 1:# 充值
                customer_object.balance += amount
            else: # 扣款
                customer_object.balance -= amount
            customer_object.save()  # 存入客户表
        # 成功后跳转回流水列表页
        return redirect('customer_charge', pk=pk)

    return render(request, 'customer_charge_add.html', {
        'form': form,
        'customer_object': customer_object
    })

