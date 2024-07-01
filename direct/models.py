from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
from django.forms import DateTimeField


# This is a Django model class named Message that represents a direct message between two users.
# This model class represents a direct message between two users, with fields for the sender, recipient, body, date,
# and read status. The send_message method creates and saves two message objects, one for the sender and one for the
# recipient.
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    body = models.TextField(max_length=600, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def send_message(from_user, to_user, body):
        sender_message = Message(
            user=from_user,
            sender=from_user,
            recipient=to_user,
            body=body,
            is_read=True)
        sender_message.save()

        recipient_message = Message(
            user=to_user,
            sender=from_user,
            body=body,
            recipient=from_user, )
        recipient_message.save()
        return sender_message

    # This function is likely used to display a list of conversations
    # for the given user, showing the recipient, last message date, and number of unread messages.
    def get_messages(user):
        users = []
        messages = Message.objects.filter(user=user).values('recipient').annotate(last=Max('date')).order_by('-last')
        for message in messages:
            users.append({
                'user': User.objects.get(pk=message['recipient']),
                'last': message['last'],
                'unread': Message.objects.filter(user=user, recipient__pk=message['recipient'], is_read=False).count()
            })
        return users
