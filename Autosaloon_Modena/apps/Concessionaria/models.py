# python
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify



class Concessionaria(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='concessionaria_profile')
        partita_iva = models.CharField(max_length=11, unique=True)
        codice_fiscale = models.CharField(max_length=16, unique=True)
        telefono = models.CharField(max_length=15, blank=True, null=True)
        indirizzo = models.CharField(max_length=255, blank=True, null=True)
        slug = models.SlugField(unique=True, blank=True, null=True, max_length=255)

        def save(self, *args, **kwargs):
            if not self.slug:
                base_slug = slugify(self.user.username)
                slug = base_slug
                num = 1
                while Concessionaria.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                    slug = f"{base_slug}-{num}"
                    num += 1
                self.slug = slug
            super().save(*args, **kwargs)

class HistoryVendute(models.Model):
        concessionaria = models.ForeignKey(User, on_delete=models.CASCADE, related_name='concessionaria_vendita')
        auto_id = models.IntegerField()
        acquirente_username = models.CharField(max_length=255, blank=True, null=True)
        auto_marca = models.CharField(max_length=255, blank=True, null=True)
        auto_modello = models.CharField(max_length=255, blank=True, null=True)
        data = models.DateTimeField(auto_now_add=True)
        prezzo_vendita = models.DecimalField(max_digits=10, decimal_places=2)

class HistoryAffittate(models.Model):
        concessionaria = models.ForeignKey(User, on_delete=models.CASCADE, related_name='concessionaria_affitto')
        affittante_username = models.CharField(max_length=255, blank=True, null=True)
        auto_id = models.IntegerField()
        auto_marca = models.CharField(max_length=255, blank=True, null=True)
        auto_modello = models.CharField(max_length=255, blank=True, null=True)
        data = models.DateTimeField(auto_now_add=True)
        data_inizio = models.DateTimeField()
        data_fine = models.DateTimeField()
        prezzo_affitto = models.DecimalField(max_digits=10, decimal_places=2)
