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



def user_or_concessionaria(request):
    if hasattr(request.user, 'user_extend_profile'):
        return "Utente", request.user.user_extend_profile.id
    elif hasattr(request.user, 'concessionaria'):
        return "Concessionaria", request.user.concessionaria.id
    return None, None



def is_possessore_auto(tipologia_possessore, id_possessore, auto):
    return (
        auto.tipologia_possessore == tipologia_possessore and
        auto.id_possessore == id_possessore
    )



def get_success_url_by_possessore(request):
    tipologia, id_possessore = user_or_concessionaria(request.user)
    if tipologia == "Utente":
        return reverse('elenco_auto_utente', kwargs={'id': id_possessore})
    elif tipologia == "Concessionaria":
        return reverse('elenco_auto_concessionaria', kwargs={'id': id_possessore})
    else:
        return reverse('home')