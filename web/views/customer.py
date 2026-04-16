import re
import random
from django.http import JsonResponse
from web import models
from utils.encrypt import md5
from django.shortcuts import render, redirect
from .forms import CustomerForm, CustomerEditForm

def customer_list(request):
    # 1. 从数据库中获取所有级别数据   连表查询
    queryset = models.Customer.objects.filter(active=1).select_related('level', 'creator')
    # 2. 渲染模板，并将数据传过去
    return render(request, 'customer_list.html', {'queryset': queryset})


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
    inistance = models.Customer.objects.filter(id=pk, active=1).first()

    if request.method == 'GET':
        form = CustomerEditForm(instance=inistance)
        return render(request, 'customer_edit.html', {'form':form})
        return render(request, 'customer_list.html', {'form':form})

    if request.method == 'POST':
        form = CustomerEditForm(data=request.POST, instance=inistance)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
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