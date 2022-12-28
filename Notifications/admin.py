from django.contrib import admin
from .models import OrderChainTelegramNotification, TelegramMessage, \
    OrganizationsRelationshipTelegramNotification, \
    SystemNotification, UserNotification


# Register your models here.
@admin.register(SystemNotification)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at')


@admin.register(UserNotification)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = ('status', 'created_at')


@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat_id', 'datetime')


@admin.register(OrderChainTelegramNotification)
class OrderChainTelegramNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'chain')


@admin.register(OrganizationsRelationshipTelegramNotification)
class OrganizationsRelationshipTelegramNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'relationship')  