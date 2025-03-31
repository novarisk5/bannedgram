from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse
from .forms import SignUpForm,PostForm,CommentForm, MessageForm
from .models import User,Post,Like,Comment, Message, Chat
from django.db import models
from django.db.models import Q

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        print(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматически входит после регистрации
            return redirect('feed')  # Перенаправление на главную страницу
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.all().order_by('-created_at')

    is_owner = request.user == user

    if is_owner and request.method == 'POST':
        if request.user != user:
            return redirect('profile', username=username)  # Запретить добавление постов в чужой профиль
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('profile', username=username)
    else:
        form = PostForm()

    return render(request, 'core/profile.html', {'user': user, 'posts': posts, 'form': form,'is_owner': is_owner,})

@login_required
def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    comment_form = CommentForm()
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'core/feed.html', {'posts': posts, 'comment_form': comment_form, 'users': users})

@login_required
def my_profile(request):
    return profile(request, request.user.username)

class CustomLoginView(LoginView):
    def get_success_url(self):
        return reverse('profile', args=[self.request.user.username])
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return redirect('feed')

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        print(request.POST)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
    return redirect('feed')

@login_required
def messenger(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'core/messenger.html', {'messages': messages})

@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            return redirect('messenger')
    else:
        form = MessageForm()
    return render(request, 'core/send_message.html', {'form': form})

@login_required
def chat_list(request):
    # Получаем все чаты, где текущий пользователь является user1 или user2
    chats = Chat.objects.filter(Q(user1=request.user) | Q(user2=request.user))
    return render(request, 'core/chat_list.html', {'chats': chats})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    messages = chat.messages.all().order_by('created_at')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat  # Привязываем сообщение к чату
            message.sender = request.user  # Указываем отправителя
            message.save()
            return redirect('chat_detail', chat_id=chat.id)
    else:
        form = MessageForm()

    return render(request, 'core/chat_detail.html', {
        'chat': chat,
        'messages': messages,
        'form': form,
    })

@login_required
def create_chat(request, user_id):
    # Получите второго пользователя
    other_user = get_object_or_404(User, id=user_id)

    # Создайте чат
    chat, created = Chat.objects.get_or_create(
        user1=request.user,
        user2=other_user,
    )

    # Перенаправьте пользователя на страницу чата
    return redirect('chat_detail', chat_id=chat.id)