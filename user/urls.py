from django.urls import path

from . import views


urlpatterns = [
    path("", views.home_view, name="home"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("upload", views.upload_view, name="upload"),
    path("shellcode", views.shellcode_view, name="shellcode"),
    path("user", views.user_view, name="user"),
    path("delete_shellcode/<int:file_id>/", views.delete_shellcode, name="delete_shellcode"),
    path("help", views.help_view, name="help"),
]