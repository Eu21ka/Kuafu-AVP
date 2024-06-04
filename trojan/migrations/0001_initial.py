# Generated by Django 4.2.11 on 2024-04-10 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TrojanList',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('chosen_plan', models.CharField(max_length=20, verbose_name='免杀方案')),
                ('shellcode_remote', models.BooleanField(default=False, verbose_name='shellcode远程分离')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='生成时间')),
                ('file_hash', models.CharField(max_length=64, verbose_name='生成文件Hash')),
            ],
        ),
    ]
