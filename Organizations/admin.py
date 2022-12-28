from django.contrib import admin
from .models import *

from django.conf.urls import url

from django.http import HttpResponse, HttpResponseRedirect

from Users.models import User, UserCompanyRelation

from Notifications.constants import TELEGRAM_BOT_TOKEN as TOKEN
import telebot


# Register your models here.


class UserFactoryInline(admin.TabularInline):
    model = Factory.users.through
    # fk_name = 'user'


class UserCompanyInline(admin.TabularInline):
    model = Company.users.through
    # fk_name = 'user'


class FactoryCompanyInline(admin.TabularInline):
    model = Company.factories.through


class WarehouseCompanyInline(admin.TabularInline):
    model = Company.warehouses.through


class CompanyRelationshipsInline(admin.TabularInline):
    model = Company.relationships.through
    fk_name = 'company_1'


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'factory', 'created_time')


@admin.register(Address)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', 'street', 'office')



@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    
    change_form_template = 'admin/model_change_form.html',    
    
    def response_change(self, request, obj):
        
        if "_notify-approve"  in request.POST or "_notify-reject" in request.POST:
            
            if "_notify-approve" in request.POST:
                text = f"Документ для подтверждения компании _{obj.name}_ принят :)"
            else:
                text = f"Документ для подтверждения компании _{obj.name}_ отклонён :("
                
            relations = UserCompanyRelation.objects.filter(company=obj,
                                                           company_info_permission=True)
            bot = telebot.TeleBot(TOKEN)
            for relation in relations:
                telegram_id = relation.user.telegram_id
                if telegram_id:
                    message = bot.send_message(
                                               telegram_id,
                                               text,
                                               parse_mode='Markdown',
                                        )
                
            return HttpResponseRedirect(".")
        
        return super().response_change(request, obj)
    
    list_display = ('name', 'email', 'company_type', 'inn', )
    search_fields = ('name', 'physical_address', 'inn')
    readonly_fields = ('id',)
    exclude = ('users', 'factories', 'warehouses', 'relationships')
    inlines = [
        UserCompanyInline,
        FactoryCompanyInline,
        WarehouseCompanyInline,
        CompanyRelationshipsInline,
    ]

    def get_fieldsets(self, request, obj=None):

        return (
            ('Information', {'fields': ('name', 'id',  'phone',
                                        'leaders', 'company_type',
                                        'rating', 'balance')}),
            ('Location', {'fields': ('physical_address', 'postal_code', 'x_coordinate', 'y_coordinate')}),
            # ('Staff', {'fields': ('users',)}),
            ('Bank requisites', {'fields': ('inn', 'kpp', 'ogrn', 'okpo', 'okved',
                                            'checking_account', 'correspondent_account', 
                                            'bik', 'legal_address')})
        )


    
@admin.register(Okved)
class OkvedAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Factory)
class FactoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company',)
    search_fields = ('name', 'address',)
    readonly_fields = ('id',)
    exclude = ('users',)
    inlines = [
        UserFactoryInline,
    ]

    def get_fieldsets(self, request, obj=None):

        return (
            ('Information', {'fields': ('name', 'id', 'company', 'website',
                                        'rating', )}),
            ('Location', {'fields': ('address', 'postal_code', 'x_coordinate', 'y_coordinate')}),
            # ('Staff', {'fields': ('users',)}),
        )

    def get_form(self, request, obj=None, **kwargs):
        exclude = ('postal_code', 'x_coordinate', 'y_coordinate', 'rating', 'id')
        kwargs.update({
            'exclude': getattr(kwargs, 'exclude', tuple()) + (exclude,)
        })
        return super(FactoryAdmin, self).get_form(request, obj, **kwargs)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('postal_code', 'x_coordinate', 'x_coordinate')


# @admin.register(CompanyAuthToken)
# class CompanyAuthTokenAdmin(admin.ModelAdmin):
#     list_display = ('key', 'user', 'created')
#     search_fields = ('user', 'key', )
#     autocomplete_fields = ('user', )


@admin.register(TokenInviteToCompany)
class TokenInviteToCompanyAdmin(admin.ModelAdmin):
    list_display = ('token', 'user', 'company', 'created_at')
    
    
    
@admin.register(TokenInviteOtherCompany)
class TokenInviteOtherCompanyAdmin(admin.ModelAdmin):
    list_display = ('token', 'company_to_invite', 'company_that_invited', 
                    'email_to_invite', 'created_at')
    
    
    
@admin.register(CompanyFile)
class CompanyFileAdmin(admin.ModelAdmin):
    list_display = ('company', 'document')
    
    
    
@admin.register(OrganizationsRelationshipFile)
class OrganizationsRelationshipFileAdmin(admin.ModelAdmin):
    list_display = ('relation', 'document')


@admin.register(CompanyProducer)
class OrganizationsRelationshipFileAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'inn')


@admin.register(FactoryProducer)
class OrganizationsRelationshipFileAdmin(admin.ModelAdmin):
    list_display = ('company_producer', 'factory', 'name')


@admin.register(OrganizationsRelationship)
class OrganizationsRelationshipADmin(admin.ModelAdmin):
    list_display = ('company_1', 'company_2', 'relationship_type')