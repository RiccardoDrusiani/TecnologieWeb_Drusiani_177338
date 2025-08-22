from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message

@login_required
def chat_view(request):
    return render(request, 'Chat/chat.html')

@login_required
def chat_list(request):
    chats = ChatRoom.objects.filter(user_1=request.user) | ChatRoom.objects.filter(user_2=request.user)
    return render(request, 'Chat/chat_list.html', {'chats': chats})

@login_required
def chat_room(request, chat_id):
    chat = get_object_or_404(ChatRoom, id=chat_id)
    messages = chat.messages.select_related('user').order_by('timestamp')
    return render(request, 'Chat/chat_room.html', {'chat': chat, 'messages': messages})
