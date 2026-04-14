from django import template
from django.conf import settings

# 实例化一个 register 对象，名字固定不能变
register = template.Library()


# 告诉 Django，把下面这个函数处理完的数据，交给 'menu.html' 去渲染
@register.inclusion_tag('menu.html')
def nb_menu(request):
    """
    生成动态左侧菜单的组件
    """
    # 1. 从 request 里拿出在中间件（第二道门）挂载的用户对象
    user_obj = request.nb_user

    # 2. 如果没拿到，或者角色不对，返回一个空列表防报错
    if not user_obj:
        return {'menu_list': []}

    # 3. 去 settings.py 里面，根据角色（ADMIN 或 CUSTOMER）拿到对应的死菜单列表
    user_menu_list = settings.NB_MENU.get(user_obj.role, [])

    # 4. 判断哪个菜单应该高亮 (动态高亮逻辑)
    current_url = request.path_info  # 拿到当前访问的 URL (比如 /level/list/)

    for item in user_menu_list:
        # 如果当前访问的 url 是以这个菜单的 url 开头的，说明我们正在看这个菜单下的内容
        # 比如访问 /level/list/ 或者 /level/add/，左侧的【级别管理】(/level/list/) 都应该高亮
        if current_url.startswith(item['url']):
            item['class'] = 'active'  # 给这个菜单项加上高亮的 CSS 类名
        else:
            item['class'] = ''

    # 5. 把加工好（带高亮标记）的菜单列表，丢给 menu.html 模板去画图
    return {'menu_list': user_menu_list}