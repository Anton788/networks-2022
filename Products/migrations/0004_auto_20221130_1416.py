# Generated by Django 3.0.6 on 2022-11-30 11:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Organizations', '0012_auto_20221120_0054'),
        ('Products', '0003_auto_20221119_2224'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productrating',
            name='user',
        ),
        migrations.AddField(
            model_name='productrating',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Organizations.Company'),
        ),
    ]
