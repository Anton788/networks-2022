from django.db import models
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string

import Services.constants.tasks as TASKS
import Services.constants.download_status as DOWNLOAD_STATUS
#from django.contrib.postgres.fields import JSONField 
from jsonfield import JSONField 

TASK_CHOICE = [
    (TASKS.CREATE_EXCEL_TABLE_FROM_PRODUCTS, "Create_excel_table_from_products"),
    (TASKS.OTHER, "Other"),
    ]

DOWNLOAD_STATUS_CHOICE = [
    (DOWNLOAD_STATUS.WAITING, "Waiting"),
    (DOWNLOAD_STATUS.IN_PROGRESS, "In progress"),
    (DOWNLOAD_STATUS.FINISHED, "Finished"),
    (DOWNLOAD_STATUS.REJECTED, "Rejected"),
]


class Task(models.Model):
    task_type = models.PositiveSmallIntegerField(choices=TASK_CHOICE,
                                    default=TASKS.OTHER)
    token = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    status = models.PositiveSmallIntegerField(choices=DOWNLOAD_STATUS_CHOICE,
                                 default=DOWNLOAD_STATUS.WAITING)
    data = JSONField()
    finished_at = models.DateTimeField(null=True, blank=True)
    progress = models.PositiveSmallIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super().save(*args, **kwargs)

    def generate_token(self):
        return get_random_string(length=10)
