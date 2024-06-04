from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse
from django.template import loader
from KuafuAVBypass import settings
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .forms import UploadFileForm
from django.http import JsonResponse
import os
import logging
from .models import UploadedFile
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseNotAllowed
import hashlib
import json
from django.views.decorators.http import require_http_methods
from .forms import CustomUserChangeForm
from django.contrib import messages
import requests


logger = logging.getLogger('django')

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
    
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True, "message": "登录成功"})
        else:
            return JsonResponse({"success": False, "message": "用户名或密码错误"})
    elif request.method == 'GET':
        return render(request, 'login.html')
    else:
        return HttpResponseNotAllowed(['POST', 'GET'])

def logout_view(request):
    logout(request)
    return render(request, 'login.html')

@login_required(login_url='/login')
def home_view(request):
    return render(request, 'home.html')

@login_required(login_url='/login')
def help_view(request):
    return render(request, 'help.html')

@login_required(login_url='/login')
def user_view(request):
    user = request.user
    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.mobile = request.POST.get('mobile')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        password = request.POST.get('password', '').strip()
        password_again = request.POST.get('password_again', '').strip()   
        ip = request.POST.get('shellcode_ip_addr')
        if ip:
            try:
                requests.get(ip, timeout=5)
            except requests.RequestException:
                return JsonResponse({"success": False, "message": "远程shellcode服务器无法正常访问！"})
        user.shellcode_ip_addr = ip 
        if password:
            if password == password_again:
                user.set_password(password)
            else:
                return JsonResponse({"success": False, "message": "两次密码输入不一致！"})
        elif password_again:
            return JsonResponse({"success": False, "message": "新密码不能为空！"})
        user.save()
        return JsonResponse({"success": True, "message": "个人信息修改成功！"})
        

    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = CustomUserChangeForm(instance=user)
            return JsonResponse({
                'form': {
                    'username': form.initial['username'],
                    'email': form.initial['email'],
                    'mobile': form.initial['mobile'],
                    'shellcode_ip_addr': form.initial['shellcode_ip_addr'],
                    'first_name': form.initial['first_name'],
                    'last_name': form.initial['last_name']
                }
            }, safe=False)
        else:
            # 如果不是 AJAX 请求，返回正常的 HTML 页面
            return render(request, 'user.html', {'user': user})

#用户上传文件
@require_POST
@csrf_exempt
def upload_view(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)  # 先不要直接保存模型
            file_instance.user = request.user  # 将当前用户设置为上传的文件的用户
            
            # 计算上传的文件的哈希值
            file_content = file_instance.file.read()
            hash_digest = hashlib.sha256(file_content).hexdigest()
            
            # 检查数据库中是否已有此哈希值
            if UploadedFile.objects.filter(hash=hash_digest, user=request.user).exists():
                return JsonResponse({"success": False, "message": "请勿重复上传相同的Shellcode！"})
            
            # 更新文件指针，准备保存
            file_instance.file.seek(0)
            file_instance.hash = hash_digest
            file_instance.save()  # 不存在重复文件，保存模型
            return JsonResponse({"success": True, "message": "Shellcode上传成功！"})
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
        return JsonResponse({"success": False, "message": "只允许POST请求！"}, status=405)

#用户查看shellocode_list
@login_required(login_url='/login')
def shellcode_view(request):
    # 获取分页参数
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 13)
    files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')

    paginator = Paginator(files, per_page)
    try:
        files_page = paginator.page(page)
    except PageNotAnInteger:
        # 如果页码不是一个整数，则显示第一页
        files_page = paginator.page(1)
    except EmptyPage:
        # 如果页码超出范围，例如9999，显示最后一页
        files_page = paginator.page(paginator.num_pages)
    # 渲染模板，传递文件和分页信息
    return render(request, 'shellcode.html', {
        'files': files_page,
    })

#用户删除shellcode文件
def delete_shellcode(request, file_id):
    if request.method == 'POST':
        try:
            file_to_delete = UploadedFile.objects.get(id=file_id)
            # 实际删除文件的逻辑可以根据您的需求变化
            file_to_delete.file.delete()
            file_to_delete.delete()
            return JsonResponse({"success": True, "message": "Shellcode删除成功!"})
        except UploadedFile.DoesNotExist:
            return JsonResponse({"success": False, "message": "Shellcode不存在！"})
    else:
        return JsonResponse({"success": False, "message": "只允许POST请求！"}, status=405)


