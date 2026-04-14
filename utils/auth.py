

class UserInfo():
    """
    用户信息的 OOP 载体
    每次请求过来，中间件都会实例化这个类，挂载到 request.nb_user 上
    """
    def __init__(self, role, name, id):
        self.role = role
        self.name = name
        self.id = id

        # 中间件在（process_view）里要计算并塞进来的
        self.menu_name = None  # 当前用户正在访问的菜单名称（用来做左侧菜单的“选中高亮”效果）
        self.text_list = []  # 面包屑导航路径（比如：首页 > 级别管理 > 添加级别）