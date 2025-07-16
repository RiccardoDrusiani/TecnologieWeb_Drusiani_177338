from PIL import Image
import os

def PillowImage(immagine, x, y):
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