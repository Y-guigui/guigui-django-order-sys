from django import forms
from web import models
from django.core.exceptions import ValidationError
from utils.encrypt import md5


class BootStrapForm(object):
    """基础Form类，统一设置格式"""

    def __init__(self, *args, **kwards):
        super().__init__(*args, **kwards)

        for name, field in self.fields.items():
            if name != 'role':
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = "请输入{}".format(field.label)



class LoginForm(BootStrapForm, forms.Form):
    role = forms.ChoiceField(
        choices=(("1", "管理员"), ("2", "用户")),
        # 后端不需要关心单选框的具体样式，只要拿到 1 或 2 即可
        error_messages={'required': '请选择您的身份'}
    )
    username = forms.CharField(
        label="用户名",
        error_messages={'required': '用户名不能为空'}
    )
    password = forms.CharField(
        label = "密码",
        error_messages={'required': '密码不能为空'}
    )


class SmsLoginForm(BootStrapForm, forms.Form):
    role = forms.ChoiceField(
        choices=(("1", "管理员"), ("2", "用户")),
        # 后端不需要关心单选框的具体样式，只要拿到 1 或 2 即可
        error_messages={'required': '请选择您的身份'}
    )
    mobile = forms.CharField(
        label="手机号",
        error_messages={'required': '手机号不能为空'}
    )
    code = forms.CharField(
        label="验证码",
        error_messages={'required': '验证码不能为空'}
    )


class LevelModelForm(forms.ModelForm):
    class Meta:
        model = models.Level
        fields = ['title', 'percent']
        # 同样，为了保持我们高级的 UI 风格，注入 CSS 样式
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入级别名称'}),
            'percent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '请输入折扣比例'}),
        }
        # 自定义中文报错信息
        error_messages = {
            'title': {
                'required': '级别名称不能为空',
                'max_length': '级别名称太长了'
            },
            'percent': {
                'required': '折扣比例不能为空',
                'invalid': '请输入有效的数字'
            }
        }


    # 局部钩子：专门校验 percent 字段
    # ==========================================
    def clean_percent(self):
        percent = self.cleaned_data.get('percent')

        if percent is not None:
            if percent < 0 or percent > 100:
                # 核心：抛出验证错误！这句话会自动塞进 form.percent.errors 里
                raise ValidationError("折扣比例必须在 0 到 100 之间呀")

        return percent


class CustomerForm(BootStrapForm, forms.ModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True), # render_value=True 保证校验失败时密码不会被清空
        error_messages = {'required': '请再次确认密码'}
    )
    class Meta:
        model = models.Customer
        fields = ['username', 'mobile', 'password', 'confirm_password', 'level']
        # 把原生的 password 字段也变成密码输入框
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }
        error_messages = {
            'username': {'required': '用户名不能为空'},
            'mobile': {'required': '手机号不能为空'},
            'password': {'required': '密码不能为空'},
            'level': {'required': '请选择客户所属级别'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 拦截 Django 默认的 "---------"
        self.fields['level'].empty_label = "请选择客户级别"

    # 专门针对 mobile 字段的局部校验钩子
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        # 2. 去数据库查询是否已经存在 active=1 的该手机号
        queryset = models.Customer.objects.filter(mobile=mobile, active=1)
        if self.instance.pk:
            # 如果是编辑操作，把当前正在编辑的这个客户自己排除掉
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            # 3. 如果查到了，抛出错误，这个错误会显示在前端输入框下方
            raise ValidationError("该手机号已经被注册使用了！")
        # 4. 如果没问题，必须把原数据返回
        return mobile

    def clean_username(self):
        username = self.cleaned_data.get('username')
        queryset = models.Customer.objects.filter(username=username, active=1)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("该用户名已经被注册使用了！")
        return username

    def clean(self):
         # 先获取父类提取到的所有清洗后的数据
        cleaned_data = super().clean()
        # 拿到两次输入的密码
        pwd = cleaned_data.get("password")
        confirm_pwd = cleaned_data.get("confirm_password")
        # 校验
        if pwd and confirm_pwd:
            if pwd != confirm_pwd:
                # 主动抛出错误，并将错误绑定到 confirm_password 字段下
                self.add_error("confirm_password", "两次输入的密码不一致！")
            else:
                cleaned_data["password"] = md5(pwd)
        return cleaned_data

class CustomerEditForm(BootStrapForm, forms.ModelForm):

    class Meta:
        model = models.Customer
        fields = ['username', 'mobile', 'level']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 将 empty_label 设置为 None，Django 就会直接渲染实际的级别数据，彻底去掉空选项
        self.fields['level'].empty_label = None

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        # 排除自己的 ID，去查有没有别人用这个手机号
        queryset = models.Customer.objects.filter(mobile=mobile, active=1).exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("该手机号已经被其他客户使用了！")
        return mobile

    def clean_username(self):
        username = self.cleaned_data.get('username')
        queryset = models.Customer.objects.filter(username=username, active=1)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("该用户名已经被注册使用了！")
        return username



class PolicyModelForm(forms.ModelForm):
    class Meta:
        model = models.PricePolicy
        fields = ['count', 'price']
        # 同样，为了保持我们高级的 UI 风格，注入 CSS 样式
        widgets = {
            'count': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '请输入产品数量'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '请输入产品价格', 'step': '0.01'}),
        }
        # 自定义中文报错信息
        error_messages = {
            'count': {
                'required': '产品数量不能为空',
                'invalid': '请输入有效的整数',
            },
            'price': {
                'required': '产品价格不能为空',
                'invalid': '请输入有效的产品价格（最多两位小数）',
            }
        }

    def clean_count(self):
        count = self.cleaned_data.get('count')
        queryset = models.PricePolicy.objects.filter(count=count)

        # 排除自己,exclude pk = self.instance.pk
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError("该数量的价格策略已存在，请换一个数量！")
        return count

