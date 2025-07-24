from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

urlpatterns = [
    # path('registrazione/', views.UserCreateView.as_view(), name='registrazione'),  # ora gestita da django-registration
    path('modifica/<slug:slug>/', views.UserUpdateView.as_view(), name='modifica_utente'),
    path('elimina/<slug:slug>/', views.UserDeleteView.as_view(), name='elimina_utente'),
    path('login/', LoginView.as_view(template_name='Utente/login.html'), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('commento/crea/', views.CommentoCreateView.as_view(), name='crea_commento'),
    path('risposta/crea/', views.RispostaCreateView.as_view(), name='crea_risposta'),
    path('segnalazione/crea/', views.SegnalazioneCreateView.as_view(), name='crea_segnalazione'),
]