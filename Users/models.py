import re
import binascii
import os
from django.utils.translation import gettext_lazy as _

from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.exceptions import ValidationError
from django.db.models.constraints import UniqueConstraint

import Users.constants.user_organization_role as USER_ORGANIZATION_ROLE

USER_FACTORY_ROLE_CHOICE = [
    (USER_ORGANIZATION_ROLE.OWNER, "Owner"),
    (USER_ORGANIZATION_ROLE.MANAGER, "Manager"),
    (USER_ORGANIZATION_ROLE.STAFF, "Staff")
]


class User(AbstractUser):
    middle_name = models.CharField(verbose_name='Middle name', max_length=150, blank=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    telephone = models.CharField(max_length=13, null=True, blank=True, unique=True)
    telegram_id = models.BigIntegerField(blank=True, null=True)

    # company_creator = models.ForeignKey('Organizations.Company', on_delete=models.CASCADE, null=True, blank=True)
    organization_account = models.BooleanField(default=False,
                                               verbose_name="Is account created for special organization")

    change_password_date = models.DateField(blank=True, null=True, verbose_name="Date of last changing password")
    #system_notifications = models.ForeignKey("UserNotification", on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # if this is new, just save
            super(User, self).save(*args, **kwargs)
        else:
            # get the original
            old = User.objects.get(id=self.pk)
            if old.telephone != self.telephone:
                self.telegram_id = None

            super(User, self).save(*args, **kwargs)

    companies = models.ManyToManyField(
        'Organizations.Company',
        through='Users.UserCompanyRelation',
        through_fields=('user', 'company'),
        related_name='user_companies',
        blank=True,
    )

    factories = models.ManyToManyField(
        'Organizations.Factory',
        through='Users.UserFactoryRelation',
        related_name='user_factories',
        blank=True,
    )

    def get_full_name_or_username(self):
        """
        Return the first_name plus the last_name, with a space in between.
        If the first_name and the last_name are blank return username.
        """
        full_name = f'{self.first_name} {self.last_name}'.strip()
        if full_name:
            return full_name
        return self.username


class UserFactoryRelation(models.Model):
    verified = models.NullBooleanField(null=True)
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE, null=True, blank=True)
    factory = models.ForeignKey('Organizations.Factory', on_delete=models.CASCADE)
    role = models.IntegerField(choices=USER_FACTORY_ROLE_CHOICE)

    # PERMISSIONS
    # Возможность добавления товара,
    product_interaction_permission = models.BooleanField(verbose_name="Can add/delete/edit products")
    # выполнять поиск, создавать заказы и выбирать цепи поставок
    create_orders_permission = models.BooleanField(verbose_name="Can search and create order")
    # редачить информацию о заводе (добавление партнеров, транспорта)
    factory_info_permission = models.BooleanField(verbose_name="Can edit information about factory")
    # добавлять других юзеров,
    add_users_permission = models.BooleanField(verbose_name="Can add new users to factory")
    # принимать/отклонять заявки на заказы
    proposal_permission = models.BooleanField(verbose_name="Can accept/reject/react on proposals")

    class Meta:
        constraints = [UniqueConstraint(fields=['user', 'factory'], name='user_factory_unique')]


class UserCompanyRelation(models.Model):
    verified = models.NullBooleanField(null=True)
    # TODO: Почему null=True, есть идея, что добавление будет происходить по ссылке
    #  (с каким-то токеном), то есть у тебя есть инфа того,
    #  как ты хочешь добавить юзера, так что ты отправляешь ему ссыль с уже готовым конфигом для прикрепления)
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE, null=True, blank=True,
                             related_name="company_user")
    creator = models.ForeignKey('Users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="company_creator")
    company = models.ForeignKey('Organizations.Company', on_delete=models.CASCADE)
    role = models.IntegerField(choices=USER_FACTORY_ROLE_CHOICE)

    # PERMISSIONS
    # Возможность добавления товара !!! [Товар от имени компании (импортер/дистрибьютор/т.д.)]
    product_interaction_permission = models.BooleanField(verbose_name="Can add/delete/edit products")
    # выполнять поиск и выбирать цепи поставок,
    ordering_permission = models.BooleanField(verbose_name="Can search and create order")
    # Возможность редачить инфу о компании
    company_info_permission = models.BooleanField(verbose_name="Can edit information about company")
    # Добавлять и удалять заводы
    factory_permission = models.BooleanField(verbose_name="Can add/delete/edit factories")
    # Добавлять других пользователей
    add_users_permission = models.BooleanField(verbose_name="Can add new users to company")
    # принимать/отклонять заявки на заказы
    proposal_permission = models.BooleanField(verbose_name="Can accept/reject/react on proposals")
    
    # УЧРЕДИТЕЛЬ
    is_leader = models.BooleanField(verbose_name="Учредитель", default=False)
    

    class Meta:
        constraints = [UniqueConstraint(fields=['user', 'company'], name='user_company_unique')]

    def __str__(self):
        return f"{self.user.username[:20]} - {self.company.name[:20]}"


class UserCompanyRelationAuthToken(models.Model):
    """
    Authorization token model for relations between users and companies.
    """
    key = models.CharField(_("Key"), max_length=60, primary_key=True)
    user = models.ForeignKey(
        'Users.UserCompanyRelation', on_delete=models.CASCADE, verbose_name=_("User and company relation")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    expired = models.DateTimeField(_("Expired"), null=True, blank=True)

    class Meta:
        verbose_name = _("User company relation auth token")
        verbose_name_plural = _("User company relation auth tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(30)).decode()

    def __str__(self):
        return self.key
