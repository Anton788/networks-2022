from django.contrib import admin
from .models import Task

# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_type', 'token', 'created_at',
                    'started_at', 'status', 'data',
                    'finished_at', 'progress')
    search_fields = ('task_type', 'token', 'created_at',
                    'started_at', 'status', 'data',
                    'finished_at', 'progress')
