from django.contrib import admin

from .models import OrderChat, ChatMessage


@admin.register(OrderChat)
class OrderChatAdmin(admin.ModelAdmin):
    list_display = ('chain', 'company_first', 'company_second', 'created_at')
    
    
    
    
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'text', 'sent_at', 'sender', 
                    'status', 'message_type')