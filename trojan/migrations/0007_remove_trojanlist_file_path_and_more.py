# Generated by Django 4.2.11 on 2024-04-10 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trojan', '0006_remove_trojanlist_shellcode_file_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trojanlist',
            name='file_path',
        ),
        migrations.AddField(
            model_name='trojanlist',
            name='shellcode_path',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='shellcode_path'),
        ),
    ]
