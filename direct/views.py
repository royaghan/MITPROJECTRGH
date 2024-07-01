from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from direct.models import Message
from django.contrib.auth.models import User
from main.models import Profile
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse


# This is a Django view function named Inbox that handles displaying the inbox page for direct messages.
# This view function retrieves all messages for the current user, marks the messages in the active thread as read,
# and passes the data to the direct.html template. The template will display the direct messages and the active thread.
@login_required(login_url='signin')
def Inbox(request):
    messages = Message.get_messages(user=request.user)

    # Pagination
    paginator_messages = Paginator(messages, 5)
    page_number_messages = request.GET.get('messagespage')
    messages_data = paginator_messages.get_page(page_number_messages)

    context = {
        'messages': messages_data,
        'directs_count': Message.objects.filter(user=request.user, is_read=False).count()
    }
    return render(request, 'direct/direct.html', context)


@login_required(login_url='signin')
def inbox(request):
    directs_count = Message.objects.filter(user=request.user, is_read=False).count()
    return render(request, 'inbox.html', {'directs_count': directs_count})


# This is a Django view function named UserSearch that handles searching for users.This view function searches for
# users based on the provided query, paginates the results, and passes them to the search_user.html template. The
# template will display the search results.

@login_required
def UserSearch(request):
    query = request.GET.get('q')
    users_paginator = None

    if query:
        users = User.objects.filter(Q(username__icontains=query))

        # Pagination
        paginator = Paginator(users, 6)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

    context = {
        'users': users_paginator,
    }

    return render(request, 'direct/search_user.html', context)


# This is a Django view function named Directs that handles displaying direct messages between the current user and a
# specified user. This view function retrieves all messages for the current user, marks the messages in the active
# thread as read, and passes the data to the direct.html template. The template will display the direct messages
# between the current user and the specified user.
@login_required(login_url='signin')
def Directs(request, username):
    user = request.user
    messages = Message.get_messages(user=request.user)
    active_direct = username
    directs = Message.objects.filter(user=user, recipient__username=username).order_by('-date')
    directs.update(is_read=True)

    for message in messages:
        if message['user'].username == username:
            message['unread'] = 0

    # Pagination for directs
    paginator_directs = Paginator(directs, 5)
    page_number_directs = request.GET.get('directspage')
    directs_data = paginator_directs.get_page(page_number_directs)

    context = {
        'directs': directs_data,
        'messages': messages,
        'active_direct': active_direct
    }

    return render(request, 'direct/direct.html', context)


# This is a Django view function named SendDirect that handles sending direct messages. This view function sends a
# direct message from the current user to the specified recipient user and redirects to the directs page for the
# recipient user
@login_required(login_url='signin')
def SendDirect(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')

    if request.method == 'POST':
        to_user = get_object_or_404(User, username=to_user_username)
        Message.send_message(from_user, to_user, body)
        return HttpResponseRedirect(reverse('directs', args=[to_user_username]))
    else:
        HttpResponseBadRequest()


# This is a Django view function named NewConversation that handles starting a new conversation with a user. This
# view function starts a new conversation with the specified user and redirects to the inbox page.It also checks to
# ensure that the sender is not sending a message to themselves.
@login_required(login_url='signin')
def NewConversation(request, username):
    from_user = request.user
    to_user = get_object_or_404(User, username=username)
    body = 'Started a new conversation'

    if from_user != to_user:
        try:
            Message.objects.create(user=from_user, sender=from_user, body=body, recipient=to_user)
        except Exception as e:
            raise e
        return redirect('inbox')


# This is a Django view function named checkDirects that checks the number of unread direct messages for the current
# user. This view function is likely used to display the number of unread direct messages in a template,
# such as a navigation bar or a notification icon.It only counts messages that are unread(is_read=False) and belong to
# the current user.
def CheckDirects(request):
    directs_count = 0
    if request.user.is_authenticated:
        directs_count = Message.objects.filter(user=request.user, is_read=False).count()
    return {'directs_count': directs_count}
