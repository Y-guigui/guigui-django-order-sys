from django.shortcuts import render, redirect
from web import models
from .forms import LevelModelForm
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def level_list(request):

    q = request.GET.get('q','')
    query_dict = {'active':1}
    if q:
        query_dict['title__contains'] = q

    data_list = models.Level.objects.filter(**query_dict).order_by('id')
    paginator = Paginator(data_list, 8)
    page_number = request.GET.get('page',1)

    try:
        queryset = paginator.page(page_number)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)

    return render(request, 'level_list.html', {
        'queryset': queryset,
        'keyword': q
    })


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
        return redirect('/level/list/')

    # 验证失败，带着错误信息返回原页面
    return render(request, 'level_add.html', {'form':form})

def level_edit(request, pk):


    row_object = models.Level.objects.filter(id=pk).first()

    if not row_object:
        return redirect('/level/list/')

    page = request.GET.get('page', '')
    q = request.GET.get('q', '')

    if request.method == 'GET':
        form = LevelModelForm(instance=row_object)
        return render(request, 'level_edit.html', {'form':form})

    # POST 请求：包含 instance 代表更新（UPDATE），不包含 instance 代表新建（INSERT）
    form = LevelModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()  # 这里会自动执行 SQL 的 UPDATE 语句
        return redirect(f'/level/list/?page={page}&q={q}')

    # 验证失败，带着错误信息返回原页面
    return render(request, 'level_edit.html', {'form': form})

def level_delete(request, pk):
    """ 删除级别 (Ajax版本) """
    exists = models.Customer.objects.filter(level_id=pk).exists()

    if exists:
        # 如果存在关联客户，返回错误信息
        return JsonResponse({"status": False, "error": "该级别下还有关联客户，无法删除！"})

    # 如果没有关联，执行删除
    models.Level.objects.filter(id=pk).update(active=0)
    return JsonResponse({"status": True})