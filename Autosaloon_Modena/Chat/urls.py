from django.urls import path
from .views import chat_list, chat_room

urlpatterns = [
    path('', chat_list, name='chat'),
    path('<int:chat_id>/', chat_room, name='chat_room'),
]
