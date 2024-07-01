from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.template import loader
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.views import generic
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, FollowersCount, Comment, Notification, LikePost
from itertools import chain
import random
from django.utils.text import slugify
from django.urls import reverse
from django.urls import resolve
from django.db.models import Q
from django.core.paginator import Paginator
from main.forms import CommentForm, PostForm, ProfileEditForm
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin, AccessMixin
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.exceptions import PermissionDenied
from urllib.parse import urlparse, urlunparse
from main.decorators import user_not_authenticated
from main.tokens import account_activation_token
from django.shortcuts import render
from django.contrib.sites.models import Site
from django.contrib.auth.backends import ModelBackend
from logging.config import valid_ident
from django import template
from django.http import JsonResponse
from django.views.generic import ListView
from direct.models import Message
import json


# It retrieves all the users that the current user is following from the FollowersCount model. It creates a list of
# the users being followed(user_following_list). It fetches all posts from the database, either from the current user
# or from users they are following, ordered by the creation date in descending order. It retrieves a list of all
# users in the system (all_users). It generates a list of new suggestions, excluding the current user and anyone they
# are already following.
@login_required(login_url='signin')
def index(request):
    directs_count = Message.objects.filter(user=request.user, is_read=False).count()
    user_following_all = FollowersCount.objects.filter(follower=request.user.username)
    user_following_list = [fc.user for fc in user_following_all]
    feed_list = Post.objects.filter(Q(user=request.user) | Q(user__in=user_following_list)).order_by('-created_at') \
        .reverse
    all_users = User.objects.all()
    new_suggestions_list = [user for user in all_users if
                            user != request.user and not FollowersCount.objects.filter(follower=request.user.username,
                                                                                       user=user)]
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        user_profile = Profile.objects.create(user=request.user)

    username_profile = []
    username_profile_list = []
    for users in new_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))
    # suggestions_username_profile_list = username_profile_list

    return render(request, 'index.html',
                  {'user_profile': user_profile, 'posts': feed_list, 'directs_count': directs_count,
                   'suggestions_username_profile_list': suggestions_username_profile_list[:4]})


# This is a Django class-based view, specifically an UpdateView, that handles the editing of a user's profile.
@login_required(login_url='signin')
class ProfileEditView(UpdateView):
    model = Profile
    form_class = ProfileEditForm
    template_name = 'profile_edit.html'

    def get_queryset(self):
        return Profile.objects.filter(pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('profile_edit', kwargs={'pk': self.get_object().pk})


# This view function retrieves all posts and the current user's profile, and passes them to the explore template
# The template will display the posts and the user's profile information.
@login_required(login_url='signin')
def explore(request):
    post = Post.objects.all().order_by('-created_at')
    profile = Profile.objects.get(user=request.user)
    for p in post:
        if not p.image:
            p.image = 'default_image.jpg'  # Set a default image
    template = loader.get_template('explore.html')
    context = {
        'post': post,
        'profile': profile

    }
    return HttpResponse(template.render(context, request))


# This is a Django view function named about_view that handles requests for the "about" page.
def about_view(request):
    return render(request, 'aboutPage.html')


# defines a view function named privacy_view that takes a request object as an argument.
def privacy_view(request):
    return render(request, 'privacy.html')


# This is a Django view function named upload that handles file uploads and creates a new Post object.
# This view function handles the upload process, creates a new Post object, and saves it to the database.
# If the request is not a POST request, it renders the upload.html template, which likely contains a form for
#     the user to upload a new post.
@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        title = request.POST['title']
        caption = request.POST['caption']

        if title == "" and caption == "":
            new_post = Post.objects.create(user=user, image=image)
        else:
            new_post = Post.objects.create(user=user, image=image, caption=caption, title=title)

        return redirect('/')
    else:
        return render(request, "upload.html")


@login_required(login_url='signin')
def get_queryset(self):
    return Post.objects.order_by('-created_at')


# This view function retrieves the user's profile information, posts, followers, and following count, and passes it
# to the profile template. It also checks if the current user is following the user and sets the button text
# accordingly.
@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context)


# This view function uses Django's built-in authentication framework and search functionality to retrieve a list of
# user profiles that match the search query.It then renders the search template with the search results.
@login_required(login_url='signin')
def search(request):
    user_object = request.user
    user_profile = Profile.objects.get(user=user_object)
    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)
        username_profile_list = []
        for user in username_object:
            username_profile_list.extend(Profile.objects.filter(user=user))
            username_profile_list = sorted(username_profile_list, key=lambda x: x.user.username)
        return render(request, 'search.html',
                      {'user_profile': user_profile, 'username_profile_list': username_profile_list})


# This view function uses Django's built-in authentication framework and redirects the user to
# the signin page if they are not logged in.
# It also uses the FollowersCount model to manage fellowships
# and redirects the user to the user's profile page after following/unfollowing.
@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/' + user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/' + user)
    else:
        return redirect('/')


# This view function updates the user's profile image, bio, and location fields based on the submitted form data. It
# uses Django's built-in file upload handling and redirects the user back to the settings page after saving the updates.
@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':

        if request.FILES.get('image') == None:
            image = user_profile.image
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.image = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.image = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('settings')
    return render(request, 'setting.html', {'user_profile': user_profile})


# This view function uses Django's built-in authentication framework to create a new user and log them in. It also
# checks for duplicate emails and usernames, displaying error messages and redirecting back to the signup page if
# necessary. This code assumes that the username, email, and password variables have been properly validated and
# sanitized before creating the new user object.

def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password,
                                                first_name=first_name, last_name=last_name)
                user.save()

                # log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')

    else:
        return render(request, 'signup.html')


def signup_redirect(request):
    messages.error(request, "Something wrong here, it may be that you already have account!")
    return redirect('index')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('index')


def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, 'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
                received activation link to confirm and complete the registration. <b>Note:</b> '
                                  'Check your spam folder.')
    else:
        messages.error(request, 'Problem sending email to {to_email}, check if you typed it correctly.')


# This view function uses Django's built-in authentication framework to authenticate and log in the user.
# It also displays an error message if the credentials are invalid and redirects the user back to the signin page.
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Credentials Invalid')
            return render(request, 'signin.html', {'error': 'Credentials Invalid'})

    else:
        return render(request, 'signin.html')


# This view function uses Django's built-in authentication framework to log out the user and redirect them to the
# signin page.logout function takes the request object as an argument and clears the user's session,
# effectively logging them out. The redirect function then sends the user to the signin page, where they can log in
# again.
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('/signin?next=/')


# This view function uses the get_object_or_404 shortcut to retrieve the Post object, and the CommentForm to validate
# and save new comments. It also checks if comments are enabled for the post and displays an empty message if the
# form is invalid. Finally, it renders the post details template with the relevant context variables.

@login_required(login_url='signin')
def PostDetails(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    comments = Comment.objects.filter(post=post).order_by('-created_at')
    form = CommentForm()  # Define form here

    if request.method == 'POST':
        if post.enabled:  # Check if comments are enabled
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = post
                comment.user = user
                comment.save()
                return HttpResponseRedirect(reverse('post-details', args=[post_id]))
        else:
            messages.info(request, '')

    return render(request, 'post_detail.html', {'post': post, 'comments': comments, 'form': form})


# This view class uses the LoginRequiredMixin to ensure that only logged-in users can access the view. It also uses
# the CommentForm to validate the comment data and creates a new Comment object with the appropriate attributes.
# Finally, it redirects the user to the post details page after creating the new comment.

class CommentReplyView(LoginRequiredMixin, View):
    def post(self, request, post_id, pk, *args, **kwargs):
        post = Post.objects.get(id=post_id)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()

        return HttpResponseRedirect(reverse('post-details', args=[post_id]))


# This view class uses the LoginRequiredMixin to ensure that only logged-in users can access the view. It also uses
# the CommentForm to validate the comment data and creates a new Comment object with the appropriate attributes.
# Finally, it redirects the user to the post details page after creating the new comment.

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'comment_delete.html'

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse_lazy('post-details', kwargs={'post_id': str(self.kwargs['post_id'])})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.user


# COMMENT DISABLE AND RE ENABLE
##############################################################

# This view function checks if the current user is the author of the post and toggles the enabled status of comments
# accordingly.
@login_required(login_url='signin')
def toggle_comments(request, post_id):
    post = Post.objects.get(id=post_id)
    post_user = User.objects.get(username=post.user)
    current_user = request.user
    if current_user.id == post_user.id:
        post.enabled = False
        post.save()
        return HttpResponse("Comments Disabled Successfully")
    else:
        return HttpResponseForbidden("You don't have Permission to Disable Comments on this post")


# This view function checks if the current user is the author of the post and enabled status of comments
# accordingly.
@login_required(login_url='signin')
def re_enable_comments(request, post_id):
    post = Post.objects.get(id=post_id)
    post_user = User.objects.get(username=post.user)
    current_user = request.user
    if current_user.id == post_user.id:
        post.enabled = True
        post.save()
        return HttpResponse("Comments Enabled Successfully")
    else:
        return HttpResponseForbidden("You don't have Permission to Enable Comments on this post")


# rest of your code to reply to the comment
##############################################################
# This view function uses the PostForm to validate and save the updated post data.
# It also displays error or info messages to the user as appropriate. The get_object_or_404 shortcut is
# used to retrieve the Post object, and the render shortcut is used to render the template with the context variables.
@login_required(login_url='signin')
def update_post(request, id):
    user = request.user
    post = get_object_or_404(Post, id=id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            # messages.success(request, 'Successfully updated post!')
            return redirect('profile', user.username)
        else:
            messages.error(request, 'Failed to update post. Please ensure the form is valid.')
    else:
        form = PostForm(instance=post)
        messages.info(request, {post.title})

    template = 'post_edit.html'
    context = {
        'form': form,
        'post': post,
    }
    return render(request, template, context)


# This view function uses the @login_required decorator to ensure that only logged-in users can access the view.
# It retrieves the Post object with the given ID, deletes it, and then redirects the user to their profile page.
@login_required(login_url='signin')
def PostDeleteView(request, id):
    post = Post.objects.get(id=id)
    post.delete()
    return redirect('/profile/' + request.user.username)


# This is a Django view function named like_post that handles liking and unliking posts.
# This view function handles the logic for liking and unliking posts, and updates the post's like count accordingly. ' \
# 'It uses the LikePost model to store ' \
# 'likes and filters them by post ID and username to check if a user has already liked a post.
@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')


# NOTIFICATIONS
##################################################################

# This view function checks if the user is authenticated, and if so, counts the number of unseen
# notifications for that user. The count is then returned as a dictionary.
# This view function is likely intended to be used as a context processor or a view that returns a JSON response,
# as it returns a dictionary with the count of unseen notifications.
# when you want to display the number of unseen notifications (e.g., in a notification badge).
# retrieves all notifications from the database that belong to the current user. The Notification model is assumed to
# have a foreign key to the User model, and the filter method is used to filter the notifications by the current user.

@login_required(login_url='signin')
def create_notification(request, notification_type, message, post=None, user=None):
    print("Create notification function called")
    if notification_type in ["like", "comment"]:
        print("Notification type: like or comment")
        notification = Notification(post=post, notification_type=notification_type, message=message)
    elif notification_type in ["follow", "unfollow"]:
        print("Notification type: follow or unfollow")
        notification = Notification(user=user, notification_type=notification_type, message=message)
    print("Notification object created:", notification)
    try:
        notification.save()
        print("Notification saved successfully!")
    except Exception as e:
        print("Error saving notification:", e)
        import pdb;
        pdb.set_trace()  # Debugger breakpoint


@login_required(login_url='signin')
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)
    notification_count = notifications.count()
    return render(request, 'template.html', {'notification_count': notification_count})


@login_required(login_url='signin')
def save_notification(request):
    sender = request.user
    user = User.objects.get(id=request.POST.get('user_id'))
    notification_types = request.POST.get('notification_types')
    notification = Notification(sender=sender, user=user, notification_types=notification_types)
    notification.save()
    return redirect('notifications')


# This view function retrieves the user's notifications, marks them as seen, and renders the notifications.'
# 'html template with the notifications. '
# 'The template will display the notifications to the user.
# The loader.get_template() function is used to load the template, and the template.
# render() method is used to render the template with the context.
# The HttpResponse object is used to return the rendered HTML as a response to the request.
@login_required(login_url='signin')
def ShowNotifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    print(len(notifications))  # Add the print statement
    Notification.objects.filter(user=user, is_seen=False).update(is_seen=True)
    template = loader.get_template('notifications.html')
    context = {'notifications': notifications, }
    return HttpResponse(template.render(context, request))


# This view function filters the notifications by ID and user, and deletes the matching notification. Then,
# it redirects the user back to the notifications page. The notification ID (noti_id) is passed as an argument to the
# view function, which is used to identify the specific notification to delete. The user is also checked to ensure
# that only the current user's notifications can be deleted.
@login_required(login_url='signin')
def DeleteNotification(request, noti_id):
    user = request.user
    Notification.objects.get(id=noti_id, user=user).delete()
    return redirect('show-notifications')


# This view function checks if the user is authenticated, and if so, counts the number of unseen
# notifications for that user. The count is then returned as a dictionary.
# This view function is likely intended to be used as a context processor or a view that returns a JSON response,
# as it returns a dictionary with the count of unseen notifications.
# when you want to display the number of unseen notifications (e.g., in a notification badge).
@login_required(login_url='signin')
def CountNotifications(request):
    count_notifications = 0
    if request.user.is_authenticated:
        count_notifications = Notification.objects.filter(user=request.user, is_seen=False).count()

    return {'count_notifications': count_notifications}


# when you want to display the total number of notifications (e.g., in a dashboard or
# notification list).
@login_required(login_url='signin')
def notification_count(request):
    count = Notification.objects.filter(user=request.user).count()
    return JsonResponse({'count': count})


######################################################################################
# This view function uses the Profile model to store a user's favorites. It checks if the post is already in the
# user's favorites and either adds or removes it accordingly. Finally, it redirects the user back to the post details
# page. Note: This view function assumes that the Profile model has a ManyToMany field named favorites that stores
# the user's favorite posts. Also, the post-details URL pattern is assumed to take a post ID as an argument
@login_required(login_url='signin')
def favorite(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)

    if profile.favorites.filter(id=post_id).exists():
        profile.favorites.remove(post)

    else:
        profile.favorites.add(post)

    return HttpResponseRedirect(reverse('post-details', args=[post_id]))


######################################################################################
# This view function uses the Profile model to store a user's favorites. It checks if the post is already in the
# user's favorites and either adds or removes it accordingly. Finally, it redirects the user back to the post details
# page. Note: This view function assumes that the Profile model has a ManyToMany field named favorites that stores
# the user's favorite posts. Also, the post-details URL pattern is assumed to take a post ID as an argument


@login_required(login_url='signin')
def favorite(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)

    if profile.favorites.filter(id=post_id).exists():
        profile.favorites.remove(post)

    else:
        profile.favorites.add(post)

    return HttpResponseRedirect(reverse('post-details', args=[post_id]))


# COMMENT LIKE AND DISLIKE
##############################################################

# This view class handles both liking and disliking comments, and also handles removing likes and dislikes if the
# user has already interacted with the comment. The LoginRequiredMixin ensures that only logged-in users can access
# this view.
class AddCommentLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)

        is_dislike = False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            comment.dislikes.remove(request.user)

        is_like = False

        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break

        if not is_like:
            comment.likes.add(request.user)

        if is_like:
            comment.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


# This view class handles both disliking and removing dislikes from comments,
# as well as removing likes if the user has already liked the comment.
# The LoginRequiredMixin ensures that only logged-in users can access this view.
class AddCommentDislike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)

        is_like = False

        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break

        if is_like:
            comment.likes.remove(request.user)

        is_dislike = False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if not is_dislike:
            comment.dislikes.add(request.user)

        if is_dislike:
            comment.dislikes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)
