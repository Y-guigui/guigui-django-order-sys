from django.shortcuts import render, redirect
from web import models
from .forms import LevelModelForm


def level_list(request):
    # 1. 从数据库中获取所有级别数据
    queryset = models.Level.objects.all()
    # 2. 渲染模板，并将数据传过去
    return render(request, 'level_list.html', {'queryset': queryset})


def level_add(request):
    if request.method == 'GET':
        form = LevelModelForm()
        return render(request, 'level_add.html', {'form':form})

    # POST 请求，接收用户提交的数据进行绑定
    form = LevelModelForm(data=request.POST)
    if form.is_valid():
        #ModelForm：验证通过后，直接调用save(),就会自动存入数据库
        # 不需要你去 form.cleaned_data 里一个个取出来再 models.Level.objects.create(...)
        # models.Level.objects.create(**form.cleaned_data)
        form.save()
        # 保存成功后跳转回列表页
        return redirect('/level/list')

    # 验证失败，带着错误信息返回原页面
    return render(request, 'level_add.html', {'form':form})

def level_edit(request, pk):
    row_object = models.Level.objects.filter(id=pk).first()

    if not row_object:
        return redirect('/level/list')

    if request.method == 'GET':
        form = LevelModelForm(instance=row_object)
        return render(request, 'level_edit.html', {'form':form})

    # POST 请求：包含 instance 代表更新（UPDATE），不包含 instance 代表新建（INSERT）
    form = LevelModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()  # 这里会自动执行 SQL 的 UPDATE 语句
        return redirect('/level/list/')

    # 验证失败，带着错误信息返回原页面
    return render(request, 'level_edit.html', {'form': form})

def level_delete(request, pk):
    """
    删除级别
    """
    exists = models.Customer.objects.filter(level_id=pk).exists()
    if not exists:
        # 找到对应的记录并删除
        models.Level.objects.filter(id=pk).delete()
    return redirect('/level/list/')