from django.db import models
from django.contrib.auth.models import User

class DiscordUser(models.Model):
    discord_snowflake = models.PositiveBigIntegerField()
    linked_user = models.ForeignKey(User, models.CASCADE)

    def __str__(self):
        return f"{self.discord_username} -> {self.linked_user}"