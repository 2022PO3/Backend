from django.db import models

from src.core.models import TimeStampMixin


class Notification(TimeStampMixin, models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    seen = models.BooleanField()
    title = models.CharField(max_length=192)
    content = models.CharField(max_length=192)

    class Meta:
        db_table = "notifications"
        app_label = "api"
