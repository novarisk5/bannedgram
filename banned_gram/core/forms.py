from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post, Comment, Message

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    avatar = forms.ImageField(required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'avatar', 'bio')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'caption']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']

