# Generated by Django 3.0.6 on 2022-11-19 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Organizations', '0010_auto_20221120_0045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='kpp',
            field=models.CharField(default=0, max_length=9, verbose_name='КПП'),
            preserve_default=False,
        ),
    ]