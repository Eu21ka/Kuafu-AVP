from django.urls import path

from . import views


urlpatterns = [
    path("create", views.create_trojan, name="create_trojan"),
    path("trojan_list", views.trojan_view, name="trojan_list"),
    path('download_file/<path:fileName>', views.download_file, name='download_file'),  # 注意这里fileName可能包含斜线，所以使用path转换器
    path("delete_trojan/<int:trojan_id>/", views.delete_trojan, name="delete_trojan"),
]