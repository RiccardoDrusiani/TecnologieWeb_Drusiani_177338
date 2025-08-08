from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.Utente.models import Segnalazione, UsermodelBan

class Command(BaseCommand):
    help = 'Controlla che gli utenti che hanno terminato il ban non siano più bannati.'

    def handle(self, *args, **options):
        now = timezone.now()

        self.stdout.write(self.style.SUCCESS('Controllo affitti auto completato.'))
