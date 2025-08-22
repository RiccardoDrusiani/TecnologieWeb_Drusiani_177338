from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model

from apps.Auto.models import Auto



class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    auto_chat = models.ForeignKey(Auto, on_delete=models.CASCADE, related_name='chat_auto', null=True, blank=True)
    user_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user_1', null=True, blank=True)
    user_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user_2', null=True, blank=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    chat = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='room_chat')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_user')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.chat.name}: {self.content[:20]}"
