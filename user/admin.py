from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import CustomUser

class CustomUserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = CustomUser
admin.site.register(CustomUser, CustomUserAdmin)