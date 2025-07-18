from .models import AutoVendita, AutoAffitto


def gestione_vendita_affitto(prezzo_vendita, prezzo_affitto, auto, original_vendita, original_affitto):
    """
    Gestisce la logica di vendita e affitto delle auto.
    Questa funzione può essere utilizzata per implementare la logica di business
    relativa alla gestione delle vendite e degli affitti delle auto.
    """
    # Implementa qui la logica per gestire le vendite e gli affitti delle auto
    # Gestione AutoVendita
    if prezzo_vendita and not original_vendita:
        AutoVendita.objects.create(auto=auto, prezzo_vendita=prezzo_vendita, venditore=auto.id_possessore)
    elif not prezzo_vendita and original_vendita:
        original_vendita.delete()
    elif prezzo_vendita and original_vendita:
        original_vendita.delete()
        AutoVendita.objects.create(auto=auto, prezzo_vendita=prezzo_vendita, venditore=auto.id_possessore)

    # Gestione AutoAffitto
    if prezzo_affitto and not original_affitto:
        AutoAffitto.objects.create(auto=auto, prezzo_affitto=prezzo_affitto, affittante=auto.id_possessore)
    elif not prezzo_affitto and original_affitto:
        original_affitto.delete()
    elif prezzo_affitto and original_affitto:
        original_affitto.delete()
        AutoAffitto.objects.create(auto=auto, prezzo_affitto=prezzo_affitto, affittante=auto.id_possessore)
