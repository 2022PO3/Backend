from django.db import models


class TimeStampMixin(models.Model):
    """
    This is an abstract class for adding time stamps, namely `created_at` and
    `updated_at`. If a model inherits from this mixin, these two fields are added in the database. Inherit in the following way: `CustomModel(TimeStampMixin, models.Model)`.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
