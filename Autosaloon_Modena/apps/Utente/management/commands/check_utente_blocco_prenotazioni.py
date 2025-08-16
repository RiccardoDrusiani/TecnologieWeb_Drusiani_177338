from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.Utente.models import UserExtendModel


class Command(BaseCommand):
    help = 'Controlla che gli utenti che hanno aspettato 24 ore possano tornare a prenotare.'

    def handle(self, *args, **options):
        now = timezone.now()
        utenti_in_attesa = UserExtendModel.objects.filter(data_fine_blocco_prenotazioni__isnull=False)
        rimossi = 0
        for utente in utenti_in_attesa:
            if utente.data_fine_blocco_prenotazioni <= now:
                utente.data_fine_blocco_prenotazioni = None
                utente.data_inizio_blocco_prenotazioni = None
                utente.save()
                rimossi += 1
        self.stdout.write(self.style.SUCCESS(f"Controllo ban utenti completato. Ban rimossi: {rimossi}"))