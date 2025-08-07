from PIL import Image
import os

from django.urls import reverse


def pillowImage(immagine, x, y):
    if immagine and os.path.exists(immagine.path):
        img = Image.open(immagine.path)
        # Ridimensiona l'immagine se supera una dimensione specifica
        max_size = (x, y)
        if img.height > x or img.width > y:
            img.thumbnail(max_size)
            img.save(immagine.path)
    else:
        img = None
    return img



def user_or_concessionaria(user):
    if user.groups.filter(name='concessionaria').exists():
        return 'Concessionaria', user.id
    elif user.groups.filter(name='utente').exists():
        return 'Utente', user.id
    return None, None



def is_possessore_auto(user, auto):
    return auto.user_auto_id == user.id



def get_success_url_by_possessore(request):
    return '/Auto/user-autos'


# Aggiungi una funzione di utilità per le scelte di disponibilità
DISPONIBILITA_CHOICES = [
    (0, "Vendita"),
    (1, "Affitto"),
    (2, "Vendita e Affitto"),
]
