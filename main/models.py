from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.conf import settings
import PIL
from PIL import Image
from datetime import datetime
from django.utils import timezone
from pyexpat import model
from django.db.models import Max
from django.utils.safestring import SafeString
from django.db.models.signals import post_save, post_delete
from django.db.models.signals import Signal
from django.utils.text import slugify
from django.urls import reverse
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

User = get_user_model()


# This is a Django model class, specifically a Profile model, that represents a user's profile.
class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    id_user = models.IntegerField(null=True, blank=True)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png', blank=True, null=True,
                              verbose_name='image')
    location = models.CharField(max_length=100, blank=True)

    # The str method is a special method in Python that returns a string representation
    # of the object.In this case, it returns a string that includes the user's
    # username and the text " - Profile".

    def __str__(self):
        return f'{self.user.username} - Profile'


# This is a Django model class, specifically a Post model, that represents a post in a social media or blogging
# application.

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=200, unique=True, null=True)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    no_of_likes = models.IntegerField(default=0)
    user = models.CharField(max_length=100)
    comments_count = models.IntegerField(default=0)
    enabled = models.BooleanField(default=True)

    # The get_absolute_url method returns the URL for the post's details page. The str method returns a string
    # representation of the post, which is the post's ID.Overall, this model is designed to store and manage posts in
    # a social media  application.
    def get_absolute_url(self):
        return reverse('post-details', args=[str(self.id)])

    def __str__(self):
        return str(self.id)

    # The Meta class is used to define metadata for the model.In this case, the ordering attribute specifies that
    # posts should be ordered in descending order by creation date (newest posts first).
    class Meta:
        ordering = ['-created_at']


# This is a Django model class, specifically a LikePost model, that represents a like on a post.
class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    # The str method returns a string representation of the LikePost instance, which is the username
    # of the user  who liked the post.
    def __str__(self):
        return self.username

    class Meta:
        unique_together = ('post_id', 'username')


# This is a Django model class, specifically a FollowersCount model, that represents the followers of a user.
class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    # The str method returns a string representation of the FollowersCount instance,which is the username of the user
    # being followed
    def __str__(self):
        return self.user


# This is a Django model class, specifically a Comment model, that represents a comment on a post.
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name='comment_likes')
    dislikes = models.ManyToManyField(User, blank=True, related_name='comment_dislikes')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    enabled = models.BooleanField(default=True)

    # This property returns a queryset of all comments that have this comment as their parent.The
    # order_by method is used to sort the comments in descending order by creation date(newest comments
    # first).The all method is used to evaluate the queryset and return a list of comments.
    @property
    def children(self):
        return Comment.objects.filter(parent=self).order_by('-created_at').all()

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False


# This model is designed to store and manage notifications for users, such as likes, comments, and follows.
# The NOTIFICATION_TYPES tuple provides a way to define different types of notifications, and
# the notification_types field allows you to store the specific type of notification. The sender and
# user fields link the notification to the relevant users, and the post field links the notification to
# the relevant post. The is_seen field allows you to track whether the notification has been seen by the user.
class Notification(models.Model):
    NOTIFICATION_TYPES = {
        1: _('Liked your Post'),
        2: _('Commented your Post'),
        3: _('Followed you'),
    }

    post = models.ForeignKey('main.Post', on_delete=models.CASCADE, related_name="notification_post", null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_from_user")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_to_user")
    notification_types = models.IntegerField(choices=list(NOTIFICATION_TYPES.items()), null=True, blank=True)
    text_preview = models.CharField(max_length=90, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def get_notification_display(self):
        if self.notification_types == 1:
            return f"{self.sender.username} Liked your post"
        elif self.notification_types == 2:
            return f"{self.sender.username} Commented on your post"
        else:
            return f"{self.sender.username} Followed you"
