# Generated by Django 3.0.6 on 2022-11-19 17:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Documents', '0004_auto_20221119_1718'),
        ('Organizations', '0006_auto_20221119_1718'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organizationsrelationshipfile',
            name='description',
        ),
        migrations.RemoveField(
            model_name='organizationsrelationshipfile',
            name='link',
        ),
        migrations.RemoveField(
            model_name='organizationsrelationshipfile',
            name='name',
        ),
        migrations.AddField(
            model_name='organizationsrelationshipfile',
            name='document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Documents.Document'),
        ),
    ]
