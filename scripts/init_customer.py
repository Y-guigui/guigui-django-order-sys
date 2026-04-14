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


# # 创建级别
# level_object = models.Level.objects.create(title="VIP", percent=90)
#
# # 创建 Customer 实例
# models.Customer.objects.create(
#     username='zhangsan',
#     password=md5('zhangsan'),  # 假设 md5 函数接收一个字符串并返回其 MD5 加密后的值
#     mobile='19999999999',
#     level = level_object,
#     creator_id = 1
# )

# models.Customer.objects.create(
#     username='lisi',
#     password=md5('lisi'),  # 假设 md5 函数接收一个字符串并返回其 MD5 加密后的值
#     mobile='19999999998',
#     level_id = 1,
#     creator_id = 1
# )