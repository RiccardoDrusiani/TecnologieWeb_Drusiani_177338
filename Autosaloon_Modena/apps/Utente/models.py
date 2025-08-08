from django.contrib.auth.models import User
from django.db import models
from PIL import Image
from django.utils.text import slugify
from ..utils import pillowImage

class UserExtendModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_extend_profile')
    data_nascita = models.DateField(blank=True, null=True)
    indirizzo = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    immagine_profilo = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=255)

    def save(self, *args, **kwargs):
        if not self.slug and self.user:
            base_slug = slugify(self.user.username if hasattr(self.user, 'username') else self.user.email)
            unique_slug = base_slug
            num = 1
            while UserExtendModel.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{num}"
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)
        if self.immagine_profilo:
            self.immagine_profilo = pillowImage(self.immagine_profilo, 300, 300)

class UserModelBan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_ban_profile')
    segnalazioni = models.IntegerField(blank=True, null=True, default=0)# Nuova colonna
    data_inizio_ban = models.DateTimeField(blank=True, null=True)
    data_fine_ban = models.DateTimeField(blank=True, null=True)
    qnt_ban = models.IntegerField(blank=True, null=True, default=0)  # Nuova colonna

class Segnalazione(models.Model):
    segnalatore = models.ForeignKey(User, on_delete=models.CASCADE, related_name='segnalazioni_inviate')
    segnalato = models.ForeignKey(User, on_delete=models.CASCADE, related_name='segnalazioni_ricevute')
    motivo = models.TextField(blank=True, null=True)
    data_segnalazione = models.DateTimeField(auto_now_add=True)
