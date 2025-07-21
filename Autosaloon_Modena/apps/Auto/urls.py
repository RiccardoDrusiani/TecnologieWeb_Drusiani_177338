from django.urls import path
from .views import (
    AutoAddView, AutoDeleteView, AutoModifyView, AutoAffittoView,
    AutoAcquistoView, AutoPrenotaView, AutoInContrattazioneView, AutoFineContrattazioneView,
    AutoDetailView
)

app_name = "Auto"

urlpatterns = [
    path('add/', AutoAddView.as_view(), name='add_auto'),
    path('<int:pk>/delete/', AutoDeleteView.as_view(), name='delete_auto'),
    path('<int:pk>/modify/', AutoModifyView.as_view(), name='modify_auto'),
    path('<int:pk>/affitto/', AutoAffittoView.as_view(), name='affitto_auto'),
    path('<int:pk>/acquisto/', AutoAcquistoView.as_view(), name='acquisto_auto'),
    path('<int:pk>/prenota/', AutoPrenotaView.as_view(), name='prenota_auto'),
    path('<int:pk>/contrattazione/', AutoInContrattazioneView.as_view(), name='contrattazione_auto'),
    path('<int:pk>/fine-contrattazione/', AutoFineContrattazioneView.as_view(), name='fine_contrattazione_auto'),
    path('<int:pk>/', AutoDetailView.as_view(), name='auto-detail'),
]