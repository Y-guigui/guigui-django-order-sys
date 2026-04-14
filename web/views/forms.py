from django import forms
from web import models
from django.core.exceptions import ValidationError


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
