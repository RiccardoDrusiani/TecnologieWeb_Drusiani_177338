from django.contrib.auth.models import User
from django.db import models
from PIL import Image
from ..utils import pillowImage

class UserExtendModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_extend_profile')
    data_nascita = models.DateField(blank=True, null=True)
    indirizzo = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    immagine_profilo = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.immagine_profilo:
            self.immagine_profilo = pillowImage(self.immagine_profilo, 300, 300)

class UserModelBan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_ban_profile')
    segnalazioni = models.IntegerField(blank=True, null=True, default=0)# Nuova colonna
    data_inizio_ban = models.DateTimeField(blank=True, null=True)
    data_fine_ban = models.DateTimeField(blank=True, null=True)
    qnt_ban = models.IntegerField(blank=True, null=True, default=0)  # Nuova colonna