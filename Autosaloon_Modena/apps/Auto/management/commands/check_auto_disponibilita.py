from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.Auto.models import Auto, AutoAffitto, AutoPrenotazione

class Command(BaseCommand):
    help = 'Controlla tutte le auto e aggiorna la disponibilità se affitto/prenotazione sono scaduti.'

    def handle(self, *args, **options):
        now = timezone.now()
        affitti = AutoAffitto.objects.filter(data_fine__lt=now)
        for affitto in affitti:
            auto = affitto.auto
            auto.disponibilita = auto.disponibilita_prec  # Disponibile per affitto
            auto.disponibilita_prec = 8
            auto.save()
            affitto.affittata = False
            affitto.affittante = None
            affitto.data_fine = None
            affitto.data_inizio = None
            affitto.save()
        prenotazioni = AutoPrenotazione.objects.filter(data_fine__lt=now)
        for prenotazione in prenotazioni:
            auto = prenotazione.auto
            auto.disponibilita = auto.disponibilita_prec  # Disponibile per affitto
            auto.disponibilita_prec = 8
            auto.save()
            prenotazione.delete()
        self.stdout.write(self.style.SUCCESS('Controllo disponibilità auto completato.'))
