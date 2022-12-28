# Generated by Django 3.0.6 on 2022-11-17 10:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Organizations', '0001_initial'),
        ('Communications', '0002_orderchat_chain'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderchat',
            name='companies',
            field=models.ManyToManyField(to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='chat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Communications.OrderChat'),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Organizations.Company'),
        ),
    ]
