from django.db import models

from Notifications.constants import USER_NOTIFICATION_STATUS

USER_NOTIFICATION_STATUS_CHOICE = [
    (USER_NOTIFICATION_STATUS.UNREAD, "unread"),
    (USER_NOTIFICATION_STATUS.READ, "read")
]


class SystemNotification(models.Model):
    title = models.CharField(verbose_name="Заголовок уведомления", max_length=50)
    description = models.CharField(verbose_name="Краткое описание уведомления", max_length=150)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    text = models.TextField(verbose_name="Текст уведомления")


class UserNotification(models.Model):
    user = models.ForeignKey("Users.User", on_delete=models.CASCADE)
    status = models.SmallIntegerField(verbose_name="Статус прочтения уведомления", choices=USER_NOTIFICATION_STATUS_CHOICE, default=USER_NOTIFICATION_STATUS.UNREAD)
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now_add=True)
    notification = models.ForeignKey("SystemNotification", on_delete=models.CASCADE)


class OrderChainTelegramNotification(models.Model):
    chain = models.ForeignKey('Orders.OrderChain', on_delete=models.SET_NULL, null=True)
    message = models.ForeignKey('Notifications.TelegramMessage', on_delete=models.SET_NULL, null=True)


class TelegramMessage(models.Model):
    user = models.ForeignKey('Users.User', on_delete=models.CASCADE)
    chat_id = models.BigIntegerField()
    message = models.BigIntegerField()  # TODO: Find in documentation of Telegram type of message id
    datetime = models.DateTimeField(auto_now_add=True)


class OrganizationsRelationshipTelegramNotification(models.Model):
    relationship = models.ForeignKey('Organizations.OrganizationsRelationship', on_delete=models.SET_NULL, null=True)
    message = models.ForeignKey('Notifications.TelegramMessage', on_delete=models.CASCADE, null=True)

