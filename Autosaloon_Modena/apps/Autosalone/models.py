from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

class Message(models.Model):
    sender_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='sent_messages')
    sender_object_id = models.PositiveIntegerField()
    sender = GenericForeignKey('sender_content_type', 'sender_object_id')

    receiver_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='received_messages')
    receiver_object_id = models.PositiveIntegerField()
    receiver = GenericForeignKey('receiver_content_type', 'receiver_object_id')

    text = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Da {self.sender} a {self.receiver}: {self.text[:30]}..."
