from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message
from django.http import HttpResponseForbidden

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
    messages = Message.objects.filter(chat=chat).order_by('timestamp')
    return render(request, 'Chat/chat_room.html', {'chat': chat, 'messages': messages})

@login_required
def chat_delete(request, chat_id):
    chat = get_object_or_404(ChatRoom, id=chat_id)
    # Solo i partecipanti possono eliminare la chat
    if chat.user_1 != request.user and chat.user_2 != request.user:
        return HttpResponseForbidden("Non sei autorizzato a eliminare questa chat.")
    if request.method == 'POST':
        chat.delete()
        return redirect('Chat:chat')
    return HttpResponseForbidden("Richiesta non valida.")
