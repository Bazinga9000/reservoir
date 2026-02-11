from django.contrib import admin

from .models import Hunt, Puzzle, Round, Answer, DiscordUser
admin.site.register(Hunt)
admin.site.register(Puzzle)
admin.site.register(Round)
admin.site.register(Answer)
admin.site.register(DiscordUser)