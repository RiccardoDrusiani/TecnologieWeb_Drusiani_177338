from django.urls import path
from . import views
from .views import ConcessionariaCreateView, ConcessionariaUpdateView, ConcessionariaDeleteView, ConcessionariaRegistrationView, ConcessionariaLoginView

urlpatterns = [
    path('aggiungi/', ConcessionariaCreateView.as_view(), name='concessionaria-create'),
    path('modifica/<slug:slug>/', ConcessionariaUpdateView.as_view(), name='concessionaria-update'),
    path('elimina/<slug:slug>/', ConcessionariaDeleteView.as_view(), name='concessionaria-delete'),
    path('registrazione/', ConcessionariaRegistrationView.as_view(), name='concessionaria-registrazione'),
    path('login/', ConcessionariaLoginView.as_view(), name='concessionaria-login'),
]