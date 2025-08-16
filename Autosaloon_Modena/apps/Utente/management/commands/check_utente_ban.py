from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.Utente.models import Segnalazione, UserModelBan

class Command(BaseCommand):
    help = 'Controlla che gli utenti che hanno terminato il ban non siano più bannati.'

    def handle(self, *args, **options):
        now = timezone.now()
        utenti_bannati = UserModelBan.objects.filter(data_fine_ban__isnull=False)
        rimossi = 0
        for ban in utenti_bannati:
            if ban.data_fine_ban <= now:
                ban.data_fine_ban = None
                ban.data_inizio_ban = None
                ban.save()
                rimossi += 1
        self.stdout.write(self.style.SUCCESS(f"Controllo ban utenti completato. Ban rimossi: {rimossi}"))
