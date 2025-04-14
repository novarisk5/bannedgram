#superuser: login: alex password: pas123

@login_required
def create_chat(request, user_id):
    try:
        other_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)

    if request.user == other_user:
        return JsonResponse({'status': 'error', 'message': 'Cannot chat with yourself'}, status=400)

    existing_chat = Chat.objects.filter(
        (Q(user1=request.user) & Q(user2=other_user)) |
        (Q(user1=other_user) & Q(user2=request.user))
    ).first()

    if existing_chat:
        return JsonResponse({
            'status': 'exists',
            'chat_id': existing_chat.id,
            'redirect_url': reverse('chat_detail', args=[existing_chat.id])
        })

    try:
        chat = Chat.objects.create(user1=request.user, user2=other_user)
        return JsonResponse({
            'status': 'success',
            'chat_id': chat.id,
            'redirect_url': reverse('chat_detail', args=[chat.id])
        })
    except Exception as e:
        logger.error(f"Failed to create chat: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to create chat'
        }, status=500)