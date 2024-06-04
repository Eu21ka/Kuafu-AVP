# Generated by Django 4.2.11 on 2024-04-11 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trojan', '0008_remove_trojanlist_shellcode_path_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='trojanlist',
            name='icon_file_name',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='icon_file_name'),
        ),
        migrations.AddField(
            model_name='trojanlist',
            name='signature_file_name',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='signature_file_name'),
        ),
        migrations.AlterField(
            model_name='trojanlist',
            name='shellcode_file_name',
            field=models.CharField(default=0, max_length=256, verbose_name='shellcode_file_name'),
            preserve_default=False,
        ),
    ]