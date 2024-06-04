from django import forms
from .models import UploadedFile
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'mobile', 'password', 'first_name', 'last_name', 'shellcode_ip_addr')


class UploadFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ('file',)


    def clean_file(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1].lower()

        # 确保只允许特定扩展名的文件上传
        if ext not in ["bin", "c", "exe"]:
            raise forms.ValidationError("仅支持上传.c、.bin和.exe格式的Shellcode文件！")

        # 设定文件大小限制，例如5MB（5 * 1024 * 1024 字节）
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

        # 检查文件大小
        if file.size > MAX_FILE_SIZE:
            raise forms.ValidationError("文件大小不能超过5MB！")
        # 返回清理后的数据很重要
        return file