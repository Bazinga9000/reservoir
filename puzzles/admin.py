from django.contrib import admin

from .models import Hunt, Puzzle, Tag, Answer, DiscordUser, AuthLink
admin.site.register(Hunt)
admin.site.register(Puzzle)
admin.site.register(Tag)
admin.site.register(Answer)
admin.site.register(DiscordUser)
admin.site.register(AuthLink)