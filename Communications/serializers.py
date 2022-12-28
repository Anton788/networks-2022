from rest_framework import serializers
from Communications.models import ChatMessage



class ReceivedChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['text', 'sent_at', 'message_type', 'metadata']


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['text', 'sent_at', 'message_type', 'metadata', 'sender']
