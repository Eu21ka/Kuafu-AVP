from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import os

import hashlib


# 定义 CustomUser 模型
class CustomUser(AbstractUser):
    mobile = models.CharField(max_length=11, verbose_name='Phone Number')
    shellcode_ip_addr = models.CharField(max_length=255, null=True,verbose_name='shellcode_ip_addr')
    # 这里可以添加更多的自定义字段...

    def __str__(self):
        return self.username
    

def user_directory_path(instance, filename):
    # 打开文件以读取其内容
    if instance.file:  # 假设file是模型字段名
        file_content = instance.file.read()
        # 使用hashlib生成文件内容的哈希值
        hash_digest = hashlib.sha256(file_content).hexdigest()
        # 取前10个字符作为文件名的一部分
        new_filename_prefix = hash_digest[:15]
    else:
        new_filename_prefix = 'default'
    base, ext = os.path.splitext(filename)
    new_filename = f"{new_filename_prefix}_{base}{ext}"
    return os.path.join("uploads", "shellcode", new_filename)


class UploadedFile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_files')
    file = models.FileField(upload_to=user_directory_path)
    hash = models.CharField(max_length=64)  # 假设使用SHA-256，长度为64个字符
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} uploaded {self.file.name} on {self.uploaded_at}"