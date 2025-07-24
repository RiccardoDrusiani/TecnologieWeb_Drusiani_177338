from django.urls import path
from django.contrib.auth.views import LoginView
from . import views
from .views import ConcessionariaCreateView, ConcessionariaUpdateView, ConcessionariaDeleteView

urlpatterns = [
    path('aggiungi/', ConcessionariaCreateView.as_view(), name='concessionaria-create'),
    path('modifica/<slug:slug>/', ConcessionariaUpdateView.as_view(), name='concessionaria-update'),
    path('elimina/<slug:slug>/', ConcessionariaDeleteView.as_view(), name='concessionaria-delete'),
    path('registrazione/', ConcessionariaCreateView.as_view(), name='concessionaria-registrazione'),
    path('login/', LoginView.as_view(template_name='Concessionaria/login.html'), name='concessionaria-login'),
]