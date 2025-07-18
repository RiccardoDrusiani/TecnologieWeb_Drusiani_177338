from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('registrazione/', views.UserCreateView.as_view(), name='registrazione'),
    path('modifica/<int:pk>/', views.UserUpdateView.as_view(), name='modifica_utente'),
    path('elimina/<int:pk>/', views.UserDeleteView.as_view(), name='elimina_utente'),
    path('login/', LoginView.as_view(template_name='Utente/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('commento/crea/', views.CommentoCreateView.as_view(), name='crea_commento'),
    path('risposta/crea/', views.RispostaCreateView.as_view(), name='crea_risposta'),
    path('segnalazione/crea/', views.SegnalazioneCreateView.as_view(), name='crea_segnalazione'),
]