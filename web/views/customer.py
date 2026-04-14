import re
import random
from django.http import JsonResponse
from web import models
from utils.encrypt import md5
from django.shortcuts import render, redirect
from .forms import LoginForm, SmsLoginForm

def customer_list(request):
    # 1. 从数据库中获取所有级别数据
    queryset = models.Customer.objects.all()
    # 2. 渲染模板，并将数据传过去
    return render(request, 'customer_list.html', {'queryset': queryset})
