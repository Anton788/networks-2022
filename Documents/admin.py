from django.contrib import admin

from .models import *


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'link', 'created_at', 'user')


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('name', 'links', 'created_at', 'user')