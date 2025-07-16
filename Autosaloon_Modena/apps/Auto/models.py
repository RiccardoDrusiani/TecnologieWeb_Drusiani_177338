from django.db import models

from ..utils import PillowImage

TIPOLOGIE_CARBURANTE = [
    (0, "Benzina"),
    (1, "Diesel"),
    (2, "Elettrico"),
    (3, "Ibrido Benzina"),
    (4, "Ibrido Diesel"),
    (5, "GPL"),
    (6, "Metano")
]

TIPOLOGIE_CAMBIO = [
    (0, "Manuale"),
    (1, "Automatico"),
    (2, "Semi-automatico")
]

TIPOLOGIE_TRAZIONE = [
    (0, "Anteriore"),
    (1, "Posteriore"),
    (2, "Integrale")
]

DISPONIBILITA = [
    (0, "Vendita"),
    (1, "Affitto"),
    (2, "Vendita e Affitto"),
    (3, "Contrattazione"),
    (4, "In Contrattazione (Venditore)"),
    (5, "In Contrattazione (Acquirente)"),
    (6, "Prenotazione"),
    (7, "Sconosciuto")
]

# Create your models here.
class Auto(models.Model):
    id_possessore = models.PositiveIntegerField()
    tipologia_possessore = models.CharField(max_length=50, choices=[(0,'Utente'), (1, 'Concessionaria')])
    marca = models.CharField(max_length=100)
    modello = models.CharField(max_length=100)
    cilindrata = models.PositiveIntegerField()
    carburante = models.IntegerField(choices=TIPOLOGIE_CARBURANTE)
    cambio = models.IntegerField(choices=TIPOLOGIE_CAMBIO)
    trazione = models.IntegerField(choices=TIPOLOGIE_TRAZIONE)
    anno = models.PositiveIntegerField()
    disponibilita = models.IntegerField(choices=DISPONIBILITA, default=5)
    chilometraggio = models.PositiveIntegerField()
    descrizione = models.TextField(blank=True, null=True)
    immagine = models.ImageField(upload_to='Auto/', blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.immagine:
            self.immagine = PillowImage(self.immagine, 300, 300)


class AutoVenditaAffitto(models.Model):
    auto = models.ForeignKey(Auto, on_delete=models.CASCADE, related_name='VenditaAffitto')
    prezzo_vendita = models.DecimalField(max_digits=10, decimal_places=2)
    prezzo_affitto = models.DecimalField(max_digits=10, decimal_places=2)
    venduta = models.BooleanField(default=False)
    affittata = models.BooleanField(default=False)
    data_pubblicazione = models.DateTimeField(auto_now_add=True)
    venditore = models.PositiveIntegerField()
    acquirente = models.PositiveIntegerField(blank=True, null=True)

class AutoContrattazione(models.Model):
    auto = models.ForeignKey(Auto, on_delete=models.CASCADE, related_name='Contrattazione')
    prezzo_iniziale = models.DecimalField(max_digits=10, decimal_places=2)
    prezzo_attuale = models.DecimalField(max_digits=10, decimal_places=2)
    prezzo_finale = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    data_inizio = models.DateTimeField(auto_now_add=True)
    data_fine = models.DateTimeField(blank=True, null=True)
    venditore = models.PositiveIntegerField()
    acquirente = models.PositiveIntegerField(blank=True, null=True)
