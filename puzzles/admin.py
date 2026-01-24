from django.contrib import admin

from .models import Hunt, Puzzle, Round, Answer
admin.site.register(Hunt)
admin.site.register(Puzzle)
admin.site.register(Round)
admin.site.register(Answer)
