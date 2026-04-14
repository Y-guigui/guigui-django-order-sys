from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect, render
from django.conf import settings
from utils.auth import UserInfo


class AuthMiddleware(MiddlewareMixin):
    """
    权限与菜单校验中间件
    """
    def process_request(self, request):
        """
        只负责校验身份（登录状态）
        """
        # 获取当前url的路径
        current_path = request.path_info
        # 白名单拦截：如果是去登录页、发短信等不需要登录的页面，直接放行
        if current_path in settings.NB_WHITE_URL:
            return None
        # 身份拦截：去 Session 里拿用户的登录凭证
        user_info_dict = request.session.get(settings.NB_SESSION_KEY)
        # 如果拿不到（没登录，或者 Session 过期了）
        if not user_info_dict:
            return redirect(settings.NB_LOGIN_URL)

        request.session_user_dict = user_info_dict
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        权限校验 & 动态菜单准备
        Django 路由匹配成功后，执行视图函数之前，会触发这里。
        """
        # 检查白名单：和第一道门一样，白名单直接放行
        current_path = request.path_info
        if current_path in settings.NB_WHITE_URL:
            return None

        # 拿取上阶段的字典数据
        user_dict = getattr(request, 'session_user_dict', None)
        if not user_dict:
            return redirect(settings.NB_LOGIN_URL)

        # 实例化 UserInfo 对象，准备挂载
        user_obj = UserInfo(
            role = user_dict['role'],
            name = user_dict["name"],
            id = user_dict['id'],
        )

        # 获取当前访问路由的名字 (name属性)
        # 例如你访问 /level/list/，这里就能拿到 "level_list"
        url_name = request.resolver_match.url_name

        # --- 核心权限校验逻辑 ---
        # 从配置中拿到当前角色的权限字典
        role_permissions = settings.NB_PERMISSION.get(user_obj.role, {})

        # 必须在拦截之前挂载，保证哪怕去到了 no_permission.html 也能显示名字和菜单
        request.nb_user = user_obj

        # 判断：你要访问的 url_name 在不在你的权限字典里
        if url_name not in role_permissions:
            # 抱歉，没有权限！返回一个友好的错误提示页面
            return render(request, 'no_permission.html', {"msg": "您没有权限访问此页面"})

        # --- 核心动态菜单逻辑 ---

        # 计算高亮菜单 (menu_name)
        # 大部分情况下，你访问的页面的 url_name 就是菜单的高亮依据
        # 假设你正在访问 'level_list'，那么左侧菜单里 url='/level/list/' 的项就应该高亮
        user_obj.menu_name = url_name

        # 计算面包屑导航 (text_list)
        # 根据你的权限字典，拿到当前页面的中文名称
        page_title = role_permissions.get(url_name)
        user_obj.text_list = ["首页", page_title]


        # 让 Django 去执行真正的 views 函数
        return None




















