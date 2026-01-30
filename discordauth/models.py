from django.db import models
from django.contrib.auth.models import User

class DiscordUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cached_username = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.cached_username}"