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

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.user.username)
            unique_slug = base_slug
            num = 1
            while Concessionaria.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

