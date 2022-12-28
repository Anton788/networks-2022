# Generated by Django 3.0.6 on 2022-11-17 10:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Products', '0001_initial'),
        ('Orders', '0002_auto_20221117_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='productrequest',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Products.Product'),
        ),
    ]
