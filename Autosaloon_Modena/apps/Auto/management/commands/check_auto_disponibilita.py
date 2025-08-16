from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timezone as dt_timezone, datetime, timedelta
from apps.Auto.models import Auto, AutoAffitto, AutoPrenotazione

class Command(BaseCommand):
    help = 'Controlla tutte le auto e aggiorna la disponibilità se affitto/prenotazione sono scaduti.'

    def handle(self, *args, **options):
        now = timezone.now().astimezone(dt_timezone.utc)
        # Debug: stampa tutte le date di AutoAffitto
        tutti_affitti = AutoAffitto.objects.all()
        for affitto in tutti_affitti:
            self.stdout.write(self.style.WARNING(f"DEBUG: id={affitto.id}, data_fine={affitto.data_fine}, affittata={affitto.affittata}"))
        affitti = AutoAffitto.objects.filter(data_fine__lt=now)
        self.stdout.write(self.style.NOTICE(f"Affitti scaduti trovati: {affitti.count()}"))
        for affitto in affitti:
            self.stdout.write(self.style.NOTICE(f"Affitto: id={affitto.id}, auto={affitto.auto.id}, data_fine={affitto.data_fine}, affittata={affitto.affittata}"))
            auto = affitto.auto
            auto.disponibilita = auto.disponibilita_prec  # Disponibile per affitto
            auto.disponibilita_prec = 8
            auto.save()
            # Resetta i campi dell'affitto
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
