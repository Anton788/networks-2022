# Generated by Django 3.0.6 on 2022-12-03 22:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Documents', '0005_photo'),
        ('Products', '0004_auto_20221130_1416'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productimage',
            name='description',
        ),
        migrations.RemoveField(
            model_name='productimage',
            name='link',
        ),
        migrations.AddField(
            model_name='productimage',
            name='photo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='photo', to='Documents.Photo'),
        ),
    ]
