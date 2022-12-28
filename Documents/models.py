from django.db import models
from jsonfield import JSONField


class Document(models.Model):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=4000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(max_length=300)
    user = models.ForeignKey('Users.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.id}. {self.name[:50]}"


class Photo(models.Model):
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    links = JSONField()
    user = models.ForeignKey('Users.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.id}. {self.name[:50]}"

