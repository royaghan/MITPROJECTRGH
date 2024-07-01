from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import LikePost, Post, follow_signal, unfollow_signal, Comment, FollowersCount, Notification
from .models import Profile
from django.contrib.auth.models import User, auth
import logging
import django.dispatch


# This code defines a signal handler that creates a Profile object for a User when the User is created.
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        print("User created:", instance)
    profile = Profile.objects.create(user=instance)
    print("Profile created:", profile)


# This code ensures that when a user likes a post, a notification is created and saved, informing the post's author
# that their post was liked.
@receiver(post_save, sender=LikePost)
def create_notification_on_like(sender, instance, created, **kwargs):
    print(instance.post, instance.user)
    if created:
        post = instance.post
    sender = instance.user
    notification = Notification(
        post=post,
        sender=sender,
        user=post.user,
        notification_type=1  # Like notification type
    )
    try:
        notification.save()
    except Exception as e:
        print(f"Error saving notification: {e}")


# When a user unlikes a post, this code creates a notification informing the post's owner that their post was unliked.
@receiver(post_delete, sender=LikePost)
def unlike_post_notification(sender, instance, **kwargs):
    print("Signal triggered!")
    post = instance.post
    sender = instance.user
    receiver = post.owner
    notification = Notification.objects.create(
        sender=sender,
        receiver=receiver,
        post=post,
        notification_type=NotificationType.UNLIKE
    )
    notification.save()


# When a user unlikes a post, this code finds and deletes the corresponding Notification object that was created when
# the post was liked. This keeps the notifications in sync with the user's actions.
@receiver(post_delete, sender=LikePost)
def create_notification_on_unlike(sender, instance, **kwargs):
    print(instance.post, instance.user)  # Add this print statement
    print("Instance:", instance)
    print("Post:", instance.post)
    print("User:", instance.user)
    print("Notifications:", Notification.objects.filter(post=instance.post, sender=instance.user, notification_type=1))
    notifications = Notification.objects.filter(
        post=post,
        sender=sender,
        notification_type=1  # Like notification type
    )
    print(notifications)  # Add this print statement
    try:
        notifications.delete()
    except Exception as e:
        logging.error(f"Error deleting notification: {e}")


# This function will create a new Notification object when a LikePost object is deleted (i.e., when a user unlikes a
# post).
@receiver(post_delete, sender=LikePost)
def create_notification_on_unlike(sender, instance, **kwargs):
    notification = Notification(
        user=instance.post.user,
        notification_type='Unlike',
        post=instance.post
    )
    notification.save()


# signal handler that sends a notification to the post owner when someone likes their post.
@receiver(post_save, sender=LikePost)
def send_notification(sender, instance, created, **kwargs):
    if created:
        notification = instance
        user = notification.user
        if user != notification.post.user:  # Check if the user who liked is not the post owner
            notification.send()


# This code defines a signal handler that listens for the deletion of a LikePost object and triggers a function to
# create a notification for the unlike action.
@receiver(post_delete, sender=LikePost)
def likepost_post_delete_handler(sender, instance, **kwargs):
    print("LikePost instance deleted!")
    create_notification_on_unlike(sender, instance, **kwargs)


@receiver(post_save, sender=FollowersCount)
def follow_signal(sender, instance, created, **kwargs):
    if created:
        follower = instance.follower
        followed = instance.followed
        # Send a notification to the followed user
        notify.send(follower, recipient=followed, verb='followed you')
        # Update the followed user's follower count
        followed.profile.follower_count += 1
        followed.profile.save()
        # Update the follower user's following count
        follower.profile.following_count += 1
        follower.profile.save()


@receiver(post_save, sender=FollowersCount)
def create_follow_notification(sender, instance, created, **kwargs):
    if created:
        create_notification(instance.follower, "follow", f"You started following {instance.user.username}")


@receiver(post_delete, sender=FollowersCount)
def create_unfollow_notification(sender, instance, **kwargs):
    create_notification(instance.follower, "unfollow", f"You stopped following {instance.user.username}")


# When a user comments on a post, this code creates a notification for the post's owner, informing them that someone
# has commented on their post.
@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    comment = instance
    post = comment.post
    text_preview = comment.body[:90]
    sender = comment.user
    notify = Notification(post=post, sender=sender, user=post.user, text_preview=text_preview, notification_type=2)
    notify.save()


@receiver(post_save, sender=Comment)
def create_comment_removed_notification(sender, instance, **kwargs):
    # Create a notification for the removed comment
    notification = Notification.objects.create(
        user=instance.post.author,
        notification_type='comment_removed',
        message=f'{instance.author} removed their comment on your post',
        post=instance.post
    )


@receiver(post_save, sender=Comment)
def create_comment_like_notification(sender, instance, created, **kwargs):
    if not created:
        if instance.likes.count() > 0:
            notify = Notification.objects.filter(post=instance.post, sender=instance.user, notification_type=2)
            notify.delete()


post_save.connect(create_notification_on_like, sender=LikePost)
post_delete.connect(create_notification_on_unlike, sender=LikePost)
post_save.connect(send_notification, sender=Notification)
post_delete.disconnect(unlike_post_notification, sender=LikePost)
post_delete.connect(unlike_post_notification, sender=LikePost)
post_save.connect(create_follow_notification, sender=Follower)
post_delete.connect(create_unfollow_notification, sender=Follower)
post_save.connect(create_comment_notification, sender=Comment)
post_delete.connect(create_comment_removed_notification, sender=Comment)
