import os
import sys
import django

# 获取当前脚本所在目录的绝对路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

# 设置 Django 配置模块的环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'day06.settings')
django.setup()  # 初始化 Django

from web import models
from utils.encrypt import md5

# 创建 Administrator 实例
# models.Administrator.objects.create(
#     username='admin',
#     password=md5('admin'),  # 假设 md5 函数接收一个字符串并返回其 MD5 加密后的值
#     mobile='18888888888'
# )

# models.Administrator.objects.create(
#     username='root',
#     password=md5('root'),  # 假设 md5 函数接收一个字符串并返回其 MD5 加密后的值
#     mobile='18888888889'
# )