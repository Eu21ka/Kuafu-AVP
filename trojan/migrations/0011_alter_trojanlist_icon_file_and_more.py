# Generated by Django 4.2.11 on 2024-04-11 14:17

from django.db import migrations, models
import trojan.models


class Migration(migrations.Migration):

    dependencies = [
        ('trojan', '0010_remove_trojanlist_icon_file_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trojanlist',
            name='icon_file',
            field=models.FileField(blank=True, null=True, upload_to=trojan.models.user_directory_path),
        ),
        migrations.AlterField(
            model_name='trojanlist',
            name='signature_file',
            field=models.FileField(blank=True, null=True, upload_to=trojan.models.user_directory_path),
        ),
    ]
