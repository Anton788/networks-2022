# Generated by Django 3.0.6 on 2022-11-19 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Organizations', '0007_auto_20221119_2045'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='kpp',
            field=models.CharField(blank=True, max_length=9, null=True, verbose_name='КПП'),
        ),
        migrations.AlterField(
            model_name='company',
            name='inn',
            field=models.CharField(blank=True, max_length=12, null=True, verbose_name='ИНН'),
        ),
    ]
