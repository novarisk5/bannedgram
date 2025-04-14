from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,get_user_model
from django.contrib.auth.views import LoginView
from django.urls import reverse
from .forms import SignUpForm,PostForm,CommentForm, MessageForm
from .models import User,Post,Like,Comment, Message, Chat
from django.db import models
from django.db.models import Q,Max
from django.views.decorators.http import require_POST

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


def chat_list(request):
    chats = Chat.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')

    for chat in chats:
        chat.last_message = chat.messages.order_by('-created_at').first()
        chat.other_user = chat.user2 if chat.user1 == request.user else chat.user1

    return render(request, 'core/chat_list.html', {'chats': chats})


@login_required
def chat_detail(request, chat_id):
    # Получаем чат и проверяем, что пользователь является участником
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in [chat.user1, chat.user2]:
        return render(request, 'core/403.html', status=403)

    # Получаем сообщения чата
    messages = Message.objects.filter(chat=chat).order_by('created_at')

    return render(request, 'core/chat_detail.html', {
        'chat': chat,
        'messages': messages,
        'other_user': chat.user2 if chat.user1 == request.user else chat.user1
    })


@login_required
def create_chat(request, user_id):
    try:
        other_user = User.objects.get(id=user_id)

        chat = Chat.objects.filter(
            Q(user1=request.user, user2=other_user) |
            Q(user1=other_user, user2=request.user)
        ).first()

        if chat:
            return JsonResponse({
                'redirect_url': reverse('chat_detail', args=[chat.id])
            })

        chat = Chat.objects.create(user1=request.user, user2=other_user)
        return JsonResponse({
            'redirect_url': reverse('chat_detail', args=[chat.id])
        })

    except User.DoesNotExist:
        return JsonResponse({
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'message': str(e)
        }, status=500)

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(
        Q(username__icontains=query) & ~Q(id=request.user.id))
    return JsonResponse({'users': list(users.values('id', 'username'))})


@login_required
def send_message(request, chat_id):
    if request.method == 'POST':
        chat = Chat.objects.get(id=chat_id)
        text = request.POST.get('text', '').strip()

        if text:
            Message.objects.create(
                chat=chat,
                sender=request.user,
                text=text
            )
        return redirect('chat_detail', chat_id=chat.id)


def search_users(request):
    query = request.GET.get('q', '')
    users = get_user_model().objects.filter(
        username__icontains=query
    ).exclude(
        id=request.user.id
    )[:10]

    results = [{
        'id': user.id,
        'username': user.username
    } for user in users]

    return JsonResponse({'users': results})
