
from django.contrib.auth.models import User
from django.db import models


class Cam(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cams",
    )
    uid = models.CharField(
        max_length=32,
        null=False,
    )
    name = models.CharField(
        max_length=250,
        null=False,
        default="",
    )
    max_pics = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Items",
        help_text="The maximum number of picture files to keep.",
    )
    max_gb = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Storage",
        help_text="Maximum storage space for picture in Gigabytes (GB).",
    )
    max_days = models.PositiveSmallIntegerField(
        default=90,
        verbose_name="Days",
        help_text="How many days to keep picture before they are deleted.",
    )

    def __str__(self):
        return 'Camera: {}'.format(self.name)

