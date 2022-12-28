# Generated by Django 3.0.6 on 2022-11-17 10:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Organizations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tokeninvitetocompany',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tokeninviteothercompany',
            name='company_that_invited',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='that_invited', to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='tokeninviteothercompany',
            name='company_to_invite',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_to_invite', to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='organizationsrelationshipfile',
            name='relation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_file', to='Organizations.OrganizationsRelationship'),
        ),
        migrations.AddField(
            model_name='organizationsrelationship',
            name='company_1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_1', to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='organizationsrelationship',
            name='company_2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_2', to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='organization',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='organization',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='organization',
            name='factory',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Organizations.Factory'),
        ),
        migrations.AddField(
            model_name='factoryproducer',
            name='company_producer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Organizations.CompanyProducer'),
        ),
        migrations.AddField(
            model_name='factoryproducer',
            name='factory',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Organizations.Factory'),
        ),
        migrations.AddField(
            model_name='factorycompanyrelation',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='factorycompanyrelation',
            name='factory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Organizations.Factory'),
        ),
        migrations.AddField(
            model_name='factory',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='factory',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='users_factory', through='Users.UserFactoryRelation', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='companyproducer',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='companyfile',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='company_file', to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='companyauthtoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Organizations.Company', verbose_name='Company'),
        ),
        migrations.AddField(
            model_name='companyaddress',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='company',
            name='factories',
            field=models.ManyToManyField(blank=True, related_name='factories_company', through='Organizations.FactoryCompanyRelation', to='Organizations.Factory'),
        ),
        migrations.AddField(
            model_name='company',
            name='legal_address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='legal_address', to='Organizations.CompanyAddress', verbose_name='Юридический адрес'),
        ),
        migrations.AddField(
            model_name='company',
            name='okved',
            field=models.ManyToManyField(blank=True, null=True, to='Organizations.Okved', verbose_name='ОКВЭД'),
        ),
        migrations.AddField(
            model_name='company',
            name='physical_address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='physical_address', to='Organizations.CompanyAddress'),
        ),
        migrations.AddField(
            model_name='company',
            name='relationships',
            field=models.ManyToManyField(blank=True, related_name='company_partners', through='Organizations.OrganizationsRelationship', to='Organizations.Company'),
        ),
        migrations.AddField(
            model_name='company',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='users_company', through='Users.UserCompanyRelation', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='company',
            name='warehouses',
            field=models.ManyToManyField(blank=True, related_name='warehouses_company', through='Organizations.WarehouseCompanyRelation', to='Organizations.Warehouse'),
        ),
    ]