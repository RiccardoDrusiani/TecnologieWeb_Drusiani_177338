from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.Auto.models import Auto, AutoAffitto, AutoListaAffitto

class Command(BaseCommand):
    help = 'Controlla le richieste di affitto e aggiorna la disponibilità delle auto.'

    def handle(self, *args, **options):
        now = timezone.now()
        richieste = AutoListaAffitto.objects.filter(data_inizio__lte=now)
        self.stdout.write(self.style.NOTICE(f"Richieste trovate: {richieste.count()}"))
        for richiesta in richieste:
            affitto = richiesta.lista_auto_affitto
            auto = affitto.auto
            self.stdout.write(self.style.NOTICE(f"Processo richiesta: Auto {auto.id}, Affitto {affitto.id}, Affittante {richiesta.affittante}"))
            auto.disponibilita_prec = auto.disponibilita
            auto.disponibilita = 7  # Affittata
            auto.save()
            affitto.affittata = True
            affitto.affittante = richiesta.affittante
            affitto.data_inizio = richiesta.data_inizio
            affitto.data_fine = richiesta.data_fine
            affitto.save()
            self.stdout.write(self.style.SUCCESS(f"Auto {auto.id} ora affittata. Riga lista eliminata."))
            richiesta.delete()
        self.stdout.write(self.style.SUCCESS('Controllo affitti auto completato.'))
