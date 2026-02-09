from django.db import models
from django.contrib.auth.models import User

class Theme(models.TextChoices):
    LATTE = "latte", "Latte"
    FRAPPE = "frappe", "Frappé"
    MACCHIATO = "macchiato", "Macchiato"
    MOCHA = "mocha", "Mocha"

class DiscordUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cached_username = models.CharField(max_length=64)

    linked_gmail = models.EmailField(blank=True, max_length=255)
    chosen_theme = models.CharField(max_length=9, choices=Theme.choices, default=Theme.MOCHA)

    def __str__(self):
        return f"{self.cached_username}"