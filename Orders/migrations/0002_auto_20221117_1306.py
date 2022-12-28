# Generated by Django 3.0.6 on 2022-11-17 10:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Organizations', '0001_initial'),
        ('Orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productrequest',
            name='company_executor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_executor_request', to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='productrequest',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='productrequest',
            name='factory_executor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='factory_executor_request', to='Organizations.Factory'),
        ),
    ]
