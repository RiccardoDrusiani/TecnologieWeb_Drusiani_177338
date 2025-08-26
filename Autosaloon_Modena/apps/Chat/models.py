from django.db import models
from django.conf import settings



class ChatRoom(models.Model):
    name = models.CharField(max_length=255)
    auto_chat = models.ForeignKey('Auto.Auto', on_delete=models.CASCADE, related_name='chat_auto', null=True, blank=True)
    user_1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chats_as_user_1', null=True, blank=True)
    user_2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chats_as_user_2', null=True, blank=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    chat = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='room_chat')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages_user')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.chat.name}: {self.content[:20]}"
