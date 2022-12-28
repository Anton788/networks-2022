import binascii
import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import int_list_validator

import Organizations.constants.company_types as COMPANY_TYPES
from django.utils.crypto import get_random_string
import Organizations.constants.organizations_relationship_type as ORGANIZATIONS_RELATIONSHIP_TYPE
# from phonenumber_field.modelfields import PhoneNumberField

from jsonfield import JSONField

COMPANY_TYPES_CHOICES = [
    (COMPANY_TYPES.PROVIDER, "Provider"),
    (COMPANY_TYPES.TRANSPORT_COMPANY, "Transport company"),
    # (COMPANY_TYPES.DISTRIBUTOR, "Distributor"),
]

ORGANIZATIONS_RELATIONSHIP_TYPE_CHOICE = [
    (ORGANIZATIONS_RELATIONSHIP_TYPE.OWNERSHIP, "Ownership"),
    (ORGANIZATIONS_RELATIONSHIP_TYPE.PARTNERSHIP, "Partnership"),
    (ORGANIZATIONS_RELATIONSHIP_TYPE.TRANSPORTATION, "Transportation"),
    (ORGANIZATIONS_RELATIONSHIP_TYPE.DISTRIBUTION, "Distribution"),
    (ORGANIZATIONS_RELATIONSHIP_TYPE.BANNED, "Banned"),
]


class Warehouse(models.Model):
    postal_code = models.IntegerField(blank=True, null=True)  # почтовый индекс
    address = models.CharField(verbose_name='Warehouse address', max_length=300, blank=True, null=True)
    x_coordinate = models.FloatField(blank=True, null=True)
    y_coordinate = models.FloatField(blank=True, null=True)


class Organization(models.Model):
    company = models.ForeignKey('Organizations.Company', on_delete=models.SET_NULL, null=True, blank=True)
    factory = models.ForeignKey('Organizations.Factory', on_delete=models.SET_NULL, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey('Users.User', on_delete=models.SET_NULL, null=True, blank=True)


class Factory(models.Model):
    company = models.ForeignKey('Organizations.Company', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(verbose_name='Factory name', max_length=100)
    description = models.CharField(max_length=8000, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(verbose_name='Factory address', max_length=300, blank=True, null=True)
    website = models.CharField(verbose_name="Factory's website", max_length=180, blank=True, null=True)
    rating = models.FloatField(default=0.0)
    #####################
    # TODO: ADD META INFO ABOUT FACTORY
    #####################
    postal_code = models.IntegerField(blank=True, null=True)  # почтовый индекс
    x_coordinate = models.FloatField(blank=True, null=True)
    y_coordinate = models.FloatField(blank=True, null=True)

    users = models.ManyToManyField(
        'Users.User',
        through='Users.UserFactoryRelation',
        through_fields=('factory', 'user'),
        related_name='users_factory',
        blank=True,
    )

    def __str__(self):
        name_len = len(self.name)
        if name_len < 15:
            return self.name
        return f"{self.name}..."


class CompanyProducer(models.Model):
    company = models.ForeignKey("Organizations.Company", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    inn = models.CharField(max_length=20, blank=True, null=True, verbose_name="ИНН/КПП")

    def __str__(self):
        return self.name + " " + self.inn


class FactoryProducer(models.Model):
    company_producer = models.ForeignKey("Organizations.CompanyProducer", on_delete=models.SET_NULL, null=True)
    factory = models.ForeignKey("Organizations.Factory", on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# class CompanyProducer(models.Model):
#     company = models.ForeignKey("Organizations.Company", on_delete=models.CASCADE, null=True)
#     name = models.CharField(max_length=100)
#     inn = models.CharField(max_length=20, blank=True, null=True, verbose_name="ИНН/КПП")
#
#
# class FactoryProducer(models.Model):
#     factory = models.ForeignKey("Organizations.Factory", on_delete=models.CASCADE, null=True)
#     name = models.CharField(max_length=100)


class Address(models.Model):
    country = models.CharField(max_length=50, verbose_name="Страна", default="")
    post_code = models.CharField(max_length=10, verbose_name="Почтовый индекс", default="")
    region = models.CharField(max_length=70, verbose_name="Область", default="")
    city = models.CharField(max_length=40, verbose_name="Город", default="")
    street = models.CharField(max_length=70, verbose_name="Улица", default="")
    house = models.CharField(max_length=20, verbose_name="Дом", default="")
    office = models.CharField(max_length=80, verbose_name="Офис", default="")

    def __str__(self):
        return f"г. {self.city}, ул. {self.street}, {self.house}"


class Okved(models.Model):
    name = models.CharField(max_length=500)
    code = models.CharField(max_length=11)  # for example 50.20.3

    def __str__(self):
        return f"{self.code}\t{self.name[:70]}"


class Company(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    email = models.EmailField(blank=True)
    # address = models.CharField(max_length=300, blank=True, null=True)
    physical_address = models.ForeignKey("Organizations.Address", on_delete=models.SET_NULL,
                                         null=True, related_name='physical_address')
    # phone = PhoneNumberField(null=True, blank=True)
    phone = models.CharField(null=True, blank=True, max_length=12, default="")
    balance = models.IntegerField(default=0, null=True, blank=True)

    inn = models.CharField(max_length=12, verbose_name="ИНН")
    kpp = models.CharField(max_length=9, blank=True, null=True, verbose_name="КПП")
    ogrn = models.CharField(max_length=13, blank=True, null=True, verbose_name="ОГРН")
    okpo = models.IntegerField(blank=True, null=True, verbose_name="ОКПО")
    # okved = models.IntegerField(blank=True, null=True, verbose_name="ОКВЭД")
    okved = models.ManyToManyField('Organizations.Okved', verbose_name="ОКВЭД")
    checking_account = models.CharField(max_length=20, blank=True, null=True, verbose_name="Р/с")
    correspondent_account = models.CharField(max_length=20, blank=True, null=True,
                                             verbose_name="Корреспондентский счет")
    bik = models.CharField(max_length=9, blank=True, null=True, verbose_name="БИК")
    legal_address = models.ForeignKey("Organizations.Address", on_delete=models.SET_NULL,
                                      null=True, verbose_name="Юридический адрес", related_name='legal_address')

    # bank_requisites = models.CharField(max_length=300, blank=True, null=True)
    # leader = models.CharField(max_length=100, blank=True, null=True)
    leaders = JSONField(default=[])
    website = models.CharField(verbose_name="Company's website", max_length=180, blank=True, null=True)
    single_factory = models.BooleanField(default=False, verbose_name='Company has only one factory')
    company_type = models.IntegerField(choices=COMPANY_TYPES_CHOICES)
    rating = models.FloatField(default=0.0)
    #####################
    # TODO: ADD META INFO ABOUT COMPANY
    #####################
    postal_code = models.IntegerField(blank=True, null=True)  # почтовый индекс
    # прокинуть отношения между юзерами сюда
    users = models.ManyToManyField(
        'Users.User',
        through='Users.UserCompanyRelation',
        through_fields=('company', 'user'),
        related_name='users_company',
        blank=True,
    )
    factories = models.ManyToManyField(
        'Organizations.Factory',
        through='Organizations.FactoryCompanyRelation',
        related_name='factories_company',
        blank=True,
    )
    warehouses = models.ManyToManyField(
        'Organizations.Warehouse',
        through='Organizations.WarehouseCompanyRelation',
        related_name='warehouses_company',
        blank=True,
    )

    relationships = models.ManyToManyField(
        'Organizations.Company',
        through='Organizations.OrganizationsRelationship',
        through_fields=('company_1', 'company_2'),
        related_name='company_partners',
        blank=True,
    )

    # хранить геометку на карте (географические координаты для примера, глянуть api Яндекс карт)
    x_coordinate = models.FloatField(blank=True, null=True)
    y_coordinate = models.FloatField(blank=True, null=True)

    def __str__(self):
        name_len = len(self.name)
        if name_len < 15:
            return self.name
        return f"{self.name}..."


class FactoryCompanyRelation(models.Model):
    company = models.ForeignKey('Organizations.Company', on_delete=models.CASCADE)
    factory = models.ForeignKey('Organizations.Factory', on_delete=models.CASCADE)
    factory_confirmed = models.NullBooleanField(null=True)
    company_confirmed = models.NullBooleanField(null=True)
    verified = models.NullBooleanField(null=True)


class OrganizationsRelationship(models.Model):
    relationship_type = models.IntegerField(
        verbose_name='Type of relationship',
        choices=ORGANIZATIONS_RELATIONSHIP_TYPE_CHOICE
    )
    company_1 = models.ForeignKey('Organizations.Company', on_delete=models.CASCADE, related_name="company_1")
    company_2 = models.ForeignKey('Organizations.Company', on_delete=models.CASCADE, related_name="company_2")
    company_1_confirmed = models.NullBooleanField(null=True)
    company_2_confirmed = models.NullBooleanField(null=True)
    verified = models.NullBooleanField(null=True)
    verified_datetime = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        first = '-'
        if self.company_1_confirmed:
            first = "+"
        elif self.company_1_confirmed is None:
            first = "?"
        second = '-'
        if self.company_2_confirmed:
            second = "+"
        elif self.company_2_confirmed is None:
            second = "?"
        return f"{self.company_1}[{first}] AND {self.company_2}[{second}]"


class WarehouseCompanyRelation(models.Model):
    warehouse = models.ForeignKey('Organizations.Warehouse', on_delete=models.CASCADE)
    company = models.ForeignKey('Organizations.Company', on_delete=models.CASCADE)


class CompanyAuthToken(models.Model):
    """
    $$$$$ DEPRECATED $$$$$$
    Authorization token model for companies.
    """
    key = models.CharField(_("Key"), max_length=60, primary_key=True)
    user = models.ForeignKey(
        'Organizations.Company', on_delete=models.CASCADE, verbose_name=_("Company")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    expired = models.DateTimeField(_("Expired"), null=True, blank=True)

    class Meta:
        verbose_name = _("Company auth token")
        verbose_name_plural = _("Company auth tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(40)).decode()

    def __str__(self):
        return self.key


class TokenInviteToCompany(models.Model):
    token = models.CharField(max_length=40)
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    company = models.ForeignKey('Organizations.Company', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super().save(*args, **kwargs)

    def generate_token(self):
        return get_random_string(length=40)


class TokenInviteOtherCompany(models.Model):
    token = models.CharField(max_length=40)
    company_to_invite = models.ForeignKey('Organizations.Company', on_delete=models.SET_NULL, null=True, 
                                          default=None, related_name="company_to_invite")
    email_to_invite = models.CharField(max_length=50)
    company_that_invited = models.ForeignKey('Organizations.Company', on_delete=models.SET_NULL, null=True,
                                             related_name="that_invited")
    created_at = models.DateTimeField(auto_now=True)
    used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super().save(*args, **kwargs)

    def generate_token(self):
        return get_random_string(length=40)


class CompanyFile(models.Model):
    
    company = models.ForeignKey('Organizations.Company', on_delete=models.SET_NULL, null=True)
    #link = models.CharField(verbose_name="Link to file", max_length=300)
    #name = models.CharField(verbose_name='File name', max_length=50, blank=True)
    #description = models.CharField(verbose_name='File description', max_length=300, blank=True)
    document = models.ForeignKey('Documents.Document', on_delete=models.SET_NULL, null=True)
    
    
    
class OrganizationsRelationshipFile(models.Model):
    
    relation = models.ForeignKey('Organizations.OrganizationsRelationship', on_delete=models.SET_NULL, null=True)
    #link = models.CharField(verbose_name="Link to file", max_length=300)
    #name = models.CharField(verbose_name='File name', max_length=50, blank=True)
    #description = models.CharField(verbose_name='File description', max_length=300, blank=True)
    document = models.ForeignKey('Documents.Document', on_delete=models.SET_NULL, null=True)