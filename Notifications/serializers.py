from rest_framework import serializers
from rest_framework.authtoken.models import Token
import json

from Notifications.models import UserNotification, SystemNotification


class GetSystemNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemNotification
        fields = ["id", "title", "text"]


class GetUserSystemNotificationSerializer(serializers.ModelSerializer):
    notification = GetSystemNotificationSerializer()

    class Meta:
        model = UserNotification
        fields = ["id", "status", "notification"]
