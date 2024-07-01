from django.contrib import admin
from .models import Profile, Post, Comment, Notification, FollowersCount
from django.utils.html import format_html


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'get_follower_count', 'get_following_count']

    @admin.display(description='Followers')
    def get_follower_count(self, obj):
        return FollowersCount.objects.filter(user=obj.user).count()

    @admin.display(description='Following')
    def get_following_count(self, obj):
        return FollowersCount.objects.filter(follower=obj.user).count()


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'id', 'created_at', 'no_of_likes', 'get_comments_count')

    @admin.display(description='Comments Count')
    def get_comments_count(self, obj):
        return obj.comments.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'body', 'created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'sender', 'post', 'notification_types', 'created_at',)
