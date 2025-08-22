from django.urls import path
from .views import (
    AutoAddView, AutoDeleteView, AutoModifyView, AutoAffittoView,
    AutoAcquistoView, AutoPrenotaView, AutoFineContrattazioneView,
    AutoDetailView, user_autos_view, AffittaAutoRiepilogoView, AutoInContrattazioneView, ContattazioneAutoView,
    ContrattazioneOffertaView
)

app_name = "Auto"

urlpatterns = [
    path('add/', AutoAddView.as_view(), name='add_auto'),
    path('<int:pk>/delete/', AutoDeleteView.as_view(), name='delete_auto'),
    path('<int:pk>/modify/', AutoModifyView.as_view(), name='modify_auto'),
    path('<int:pk>/affitto/', AutoAffittoView.as_view(), name='affitto_auto'),
    path('<int:pk>/acquisto/', AutoAcquistoView.as_view(), name='acquisto_auto'),
    path('<int:pk>/prenota/', AutoPrenotaView.as_view(), name='prenota_auto'),
    path('<int:pk>/fine-contrattazione/', AutoFineContrattazioneView.as_view(), name='fine_contrattazione_auto'),
    path('<int:pk>/', AutoDetailView.as_view(), name='auto-detail'),
    path('user-autos/', user_autos_view, name='user_autos'),
    path('<int:pk>/affitta/', AffittaAutoRiepilogoView, name='affitta_auto'),
    path('<int:pk>/contrattazione/', AutoInContrattazioneView.as_view(), name='contrattazione_auto_inCorso'),
    path('<int:pk>/contrattazione_view/', ContattazioneAutoView, name='contrattazione_auto_view'),
    path('offerta/<int:pk>/update/', ContrattazioneOffertaView.as_view(), name='contrattazione_offerta_update'),
]
