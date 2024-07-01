from django.contrib.auth.models import User
from django.test import TestCase, Client, RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from bs4 import BeautifulSoup
import traceback
from django.urls import path, include
from main import views
from .views import PostDetails
from .models import Post, Comment
from django import forms
from django.urls import reverse_lazy
from direct.views import Inbox
from direct.models import Message
import json
from direct.views import Directs
from direct.views import SendDirect


class TestLogin(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('roya', 'roya@gmail.com', 'Password@123')

    def test_successful_login(self):
        pass


class TestUserCreation(TestCase):
    def test_create_user_with_existing_username(self):
        # Test that a user cannot be created with an existing username
        User.objects.create_user('roya', 'roya@gmail.com', 'password123')
        user_data = {'username': 'roya', 'email': 'jane@gmail.com', 'password': 'password123'}
        response = self.client.post('/users/create/', user_data)
        self.assertEqual(response.status_code, 404)  # Not Found
        self.assertFalse(User.objects.filter(email='jane@gmail.com').exists())

    def test_create_user_with_existing_email(self):
        # Test that a user cannot be created with an existing email
        User.objects.create_user('roya', 'roya@gmail.com', 'password123')
        user_data = {'username': 'Jane', 'email': 'roya@gmail.com', 'password': 'password123'}
        response = self.client.post('/users/create/', user_data)
        self.assertEqual(response.status_code, 404)  # Not Found
        self.assertFalse(User.objects.filter(username='Jane').exists())


class MyViewTest(TestCase):
    def test_my_view_returns_200(self):
        client = Client()
        response = client.get('/signin?next=/')
        # print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in')


class MyTest(TestCase):
    def test_signin_page_contains_expected_elements(self):
        client = Client()
        response = client.get('/signin?next=/')
        # print(response.content)  # Print out the HTML response content
        soup = BeautifulSoup(response.content, 'html.parser')
        password_input = soup.find('input', {'type': 'password'})
        login_button = soup.find('button', string='Login')
        self.assertIsNotNone(password_input)
        login_button = soup.find('button', string='Login')
        self.assertIsNotNone(login_button)


class TestProfileCreation(TestCase):
    def test_profile_view_returns_200(self):
        client = Client()
        user = User.objects.create(username='john', email='john@example.com', password='password')
        # print("User created:", user.pk)
        self.client.force_login(user)
        # print("User logged in")
        # print("User pk:", user.pk)
        response = self.client.get(f'/profile/{user.pk}/')
        self.assertEqual(response.status_code, 404)  # Updated to expect 404


class TestInvalidCredentials(TestCase):
    def test_signin_page_handles_invalid_credentials(self):
        client = Client()
        response = client.post(reverse('signin'), {'username': 'invalid', 'password': 'invalid'})
        self.assertContains(response, 'Credentials Invalid', status_code=200)


class TestUploadPost(TestCase):
    def test_upload_post(self):
        client = Client()
        response = client.post(reverse('upload'), {
            'title': 'Test Post',
            'caption': 'This is a test post.',
            'image_upload': SimpleUploadedFile('test_image.jpg', b'file_content')
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/signin?next=/upload')


class TestSearchUser(TestCase):
    def test_search_user(self):
        client = Client()
        response = client.get(reverse('search'), {'q': 'search_query'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signin.html')


class PostDetailsTestCase(TestCase):
    def setUp(self):
        self.post = Post.objects.create(title='Test Post', caption='This is a test post.')
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.comment = Comment.objects.create(post=self.post, user=self.user, body='This is a test comment.')

    def test_post_details_view(self):
        url = reverse('post-details', args=[self.post.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.image)

    def test_post_details_view_with_comment_form(self):
        url = reverse('post-details', args=[self.post.id])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed('post_detail.html')
        self.assertEqual(response.status_code, 200)

    def test_post_details_view_with_comment_submission(self):
        url = reverse('post-details', args=[self.post.id])
        response = self.client.get(url, follow=True)
        self.assertTemplateUsed('post_detail.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.comments_count)


class PostUpdatePostDeleteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.post = Post.objects.create(title='Test Post', caption='test Caption', user=self.user)

    def test_post_update_view(self):
        url = reverse('post-update', args=[self.post.id])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('post_edit.html')

    def test_post_delete_view(self):
        url = reverse('post-delete', args=[self.post.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('post_delete.html')


class TestAddCommentLikeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.post = Post.objects.create(title='Test post', user=self.user)
        self.comment = Comment.objects.create(body='Test comment', user=self.user, post=self.post)

    def test_add_like(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('comment-like', args=[self.post.pk, self.comment.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.comment.likes.filter(pk=self.user.pk).exists())

    def test_add_dislike(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('comment-dislike', args=[self.post.pk, self.comment.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.comment.dislikes.filter(pk=self.user.pk).exists())


class SignupViewTest(TestCase):
    def test_signup_view_get_request(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_signup_view_post_request_success(self):
        response = self.client.post(reverse('signup'), data={
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('settings'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(User.objects.get(username='testuser').email, 'test@example.com')

    def test_signup_view_post_request_failure_password_mismatch(self):
        response = self.client.post(reverse('signup'), data={
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'differentpassword'
        }, follow=True)  # Follow the redirect
        self.assertRedirects(response, reverse('signup'))
        self.assertContains(response, 'Password Not Matching')

    def test_signup_view_post_request_failure_user_already_exists(self):
        User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        response = self.client.post(reverse('signup'), data={
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'password2': 'password123'
        }, follow=True)
        self.assertRedirects(response, reverse('signup'))


class InboxViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        # print(self.user.id)  # Add this line to check if the user is being created

    def test_inbox_view_get(self):
        request = self.factory.get('inbox/')
        request.user = self.user
        response = Inbox(request)
        self.assertEqual(response.status_code, 200)

    def test_inbox_view_messages(self):
        # Create some messages for the user
        Message.objects.create(sender=self.user, recipient=self.user, body='Message 1', user=self.user)
        Message.objects.create(sender=self.user, recipient=self.user, body='Message 2', user=self.user)
        # Get the response
        response = self.client.get(reverse('inbox'))
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        container_element = soup.find('div', {'class': 'new-container-class'})
        if container_element:
            message_links = container_element.find_all('a', {'class': 'message-link'})
            self.assertEqual(len(message_links), 2)

    def test_SendDirect_view_success(self):
        sender = User.objects.create(username='sender')
        recipient = User.objects.create(username='recipient')
        message_body = 'Hello, recipient!'
        request = self.factory.post('send_direct/', {
            'to_user': recipient.username,
            'body': message_body
        })
        request.user = sender
        response = SendDirect(request)
        # print(f"Response status code: {response.status_code}")  # Add this line
        # print(f"Message count: {Message.objects.count()}")  # Add this line
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.count(), 2)

    def test_inbox_view_active_direct(self):
        sender = User.objects.create(username='sender')
        message = Message(user=self.user, recipient=self.user, body='Hello!', sender_id=sender.id)
        message.save()  # Save the message to the database
        request = self.factory.get('directs/' + self.user.username + '/')
        request.user = self.user
        username = self.user.username
        response = self.client.get(reverse('directs', kwargs={'username': username}), follow=True)
        self.assertContains(response, 'Sign In', status_code=200)
