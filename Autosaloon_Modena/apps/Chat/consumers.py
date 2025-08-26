import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, ChatRoom
from django.contrib.auth import get_user_model

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.chat_id = self.scope['url_route']['kwargs']['chat_id']
            self.room_group_name = f'chat_{self.chat_id}'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logging.info(f"WebSocket connesso alla chat {self.chat_id}")
        except Exception as e:
            logging.error(f"Errore in connect: {e}")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user = self.scope["user"]
        if user.is_authenticated:
            await self.save_message(user, message, self.chat_id)
            username = user.username
        else:
            username = "Anonimo"
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))

    @database_sync_to_async
    def save_message(self, user, message, chat_id):
        try:
            chat = ChatRoom.objects.get(id=chat_id)
            Message.objects.create(user=user, content=message, chat=chat)
        except Exception as e:
            logging.error(f"Errore in save_message: {e}")
            raise
