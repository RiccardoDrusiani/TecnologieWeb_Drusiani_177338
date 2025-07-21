from django.urls import path
from . import views
from .views import MessageCreateView, MessageListView, MessageDetailView

urlpatterns = [
    path('', views.home, name='home'),
    path('messaggi/', MessageListView.as_view(), name='message-list'),
    path('messaggi/nuovo/', MessageCreateView.as_view(), name='message-create'),
    path('messaggi/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),
]