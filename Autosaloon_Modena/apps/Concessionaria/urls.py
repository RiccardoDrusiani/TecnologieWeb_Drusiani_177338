from django.urls import path
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordChangeDoneView
from . import views
from .views import ConcessionariaCreateView, ConcessionariaUpdateView, ConcessionariaDeleteView

urlpatterns = [
    path('aggiungi/', ConcessionariaCreateView.as_view(), name='concessionaria-create'),
    path('modifica/<slug:slug>/', ConcessionariaUpdateView.as_view(), name='concessionaria-update'),
    path('elimina/<slug:slug>/', ConcessionariaDeleteView.as_view(), name='concessionaria-delete'),
    path('registrazione/', ConcessionariaCreateView.as_view(), name='concessionaria-registrazione'),
    path('login/', LoginView.as_view(template_name='Concessionaria/login.html'), name='concessionaria-login'),
    path('impostazioni/', views.impostazioni_concessionaria, name='impostazioni_concessionaria'),
    path('password_change/', PasswordChangeView.as_view(
        template_name='Concessionaria/password_change_form.html',
        success_url = '/Concessionaria/password_change/done/'
    ), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(
        template_name='Concessionaria/password_change_done.html'
    ), name='password_change_done'),
]
