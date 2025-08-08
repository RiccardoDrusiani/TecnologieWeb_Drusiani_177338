from .models import AutoVendita, AutoAffitto, AutoListaAffitto


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

def check_affittata_in_periodo (auto, data_inizio, data_fine):
    """
    Controlla se l'auto è affittata in un determinato periodo.
    """
    print("data_inizio:", data_inizio)
    print("data_fine:", data_fine)
    affitti = AutoListaAffitto.objects.filter(lista_auto_affitto=auto, data_inizio__lte=data_fine, data_fine__gte=data_inizio)
    print("Queryset affitti:", affitti)
    print("Numero affitti trovati:", affitti.count())
    for affitto in affitti:
        print(f"Affitto trovato: id={affitto.id}, auto={affitto.auto_id}, data_inizio={affitto.data_inizio}, data_fine={affitto.data_fine}")
    return affitti.exists()
