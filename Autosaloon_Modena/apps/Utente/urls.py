app_name = "Utente"
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.urls import path, reverse_lazy
from . import views
from .views import UserCreateView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),
    # path('registrazione/', views.UserCreateView.as_view(), name='registrazione'),  # ora gestita da django-registration
    path('modifica/<slug:slug>/', views.UserUpdateView.as_view(), name='modifica_utente'),
    path('elimina/<slug:slug>/', views.UserDeleteView.as_view(), name='elimina_utente'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('commento/crea/', views.CommentoCreateView.as_view(), name='crea_commento'),
    path('risposta/crea/', views.RispostaCreateView.as_view(), name='crea_risposta'),
    path('segnalazione/crea/', views.SegnalazioneCreateView.as_view(), name='crea_segnalazione'),
    path('impostazioni/', views.impostazioni_utente, name='impostazioni_utente'),
    path('password_change/', PasswordChangeView.as_view(
        template_name='Utente/password_change_form.html',
        success_url = '/Utente/password_change/done/'
    ), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(
        template_name='Utente/password_change_done.html'
    ), name='password_change_done'),
    path('gestione-auto/', views.gestione_auto_view, name='gestione_auto'),

]