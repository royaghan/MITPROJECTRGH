from django.contrib import admin
from direct.models import Message


# registers the Message model with the Django administration site.

@admin.register(Message)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipient','body','date',)
