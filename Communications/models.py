from django.db import models

# Create your models here.
import Communications.constants.message_status as MESSAGE_STATUS
import Communications.constants.message_type as MESSAGE_TYPE
from jsonfield import JSONField

MESSAGE_STATUS_CHOICES = [
    (MESSAGE_STATUS.CREATED, "Created"),
    (MESSAGE_STATUS.SENT, "Sent"),
    (MESSAGE_STATUS.RECEIVED, "Received"),
    (MESSAGE_STATUS.READ, "Read"),
]

MESSAGE_TYPE_CHOICES = [
    (MESSAGE_TYPE.MESSAGE, "Message"),
    (MESSAGE_TYPE.NOTIFICATION, "Notification"),
]
    
    
class OrderChat(models.Model):
    
   # company_2 = models.ForeignKey('Organizations.Company', on_delete=models.SET_NULL, null=True,
                                  #related_name='company_2')
    chain = models.ForeignKey('Orders.OrderChain', on_delete=models.CASCADE)
    companies = models.ManyToManyField('Organizations.Company')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def company_first(self):
        try:
            return self.companies.all()[0]
        except:
            return None
    
    def company_second(self):
        try:
            return self.companies.all()[1]
        except:
            return None
        
    def __str__(self):
        return str(self.id)
    
    
class ChatMessage(models.Model):
    chat = models.ForeignKey('Communications.OrderChat', on_delete=models.CASCADE)
    #chain = models.ForeignKey('Orders.OrderChain', on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    sent_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey('Organizations.Company', on_delete=models.SET_NULL, null=True)
    #if_admin_message = models.BooleanField(default=False)
    status = models.PositiveSmallIntegerField(default=MESSAGE_STATUS.CREATED, choices=MESSAGE_STATUS_CHOICES)
    message_type = models.PositiveSmallIntegerField(default=MESSAGE_TYPE.MESSAGE, choices=MESSAGE_TYPE_CHOICES)
    metadata = JSONField()

    class Meta:
        ordering = ['-sent_at']