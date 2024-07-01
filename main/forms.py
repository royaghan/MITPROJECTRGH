from django.contrib.auth.models import User
from django import forms
from .models import Post, Comment, Profile
from django.db import models
from crispy_forms.helper import FormHelper
from django.urls import reverse
from django.forms import ClearableFileInput
from django_summernote.widgets import SummernoteWidget


# This is a Django form class, specifically a ModelForm, for creating and editing Post instances.
class PostForm(forms.ModelForm):  # This defines a new form class, PostForm, that inherits from Django's
    # built-in ModelForm class.
    class Meta:    # This inner class defines metadata for the form.
        model = Post   # This specifies that the form is for creating/editing Post instances.
        exclude = ('no_of_likes', 'id', 'user', 'comments_count')
        widgets = {
            'image': SummernoteWidget(),
        }


# This is a Django form class, specifically a ModelForm, for creating and editing Comment instances.
class CommentForm(forms.ModelForm):
    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'rows': '3',
            'placeholder': 'Write your Comments...'
        }))

    class Meta:
        model = Comment
        fields = ("body",)


# This is a Django form class, specifically a ModelForm, for editing Profile instances.

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'bio']  # add your fields here

    def test_func(self):
        obj = Profile.objects.get(pk=self.kwargs['pk'])
        return obj.user == self.request.user

    def get_success_url(self):
        return reverse_lazy("profile_edit", kwargs={'pk': self.object.id})