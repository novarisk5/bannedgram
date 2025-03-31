from django.urls import path
from .views import CustomLoginView
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.my_profile, name='my_profile'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chats/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('create_chat/<int:user_id>/', views.create_chat, name='create_chat'),
    # path('messenger/', views.messenger, name='messenger'),
    # path('send_message/', views.send_message, name='send_message'),
    path('<str:username>/', views.profile, name='profile'),
]