from .models import AutoVendita, AutoAffitto, AutoListaAffitto


def gestione_vendita_affitto(prezzo_vendita, prezzo_affitto, auto, original_vendita, original_affitto):
    try:
        auto_vendita = AutoVendita.objects.get(auto=auto)
    except AutoVendita.DoesNotExist:
        auto_vendita = None
    try:
        auto_affitto = AutoAffitto.objects.get(auto=auto)
    except AutoAffitto.DoesNotExist:
        auto_affitto = None

    if auto.disponibilita == 0:
        print('Acquisto')
        if auto_vendita is None:
            auto_vendita = AutoVendita.objects.create(auto=auto, prezzo_vendita=prezzo_vendita, venditore=auto.id_possessore)
        else:
            if auto_vendita is not None and auto_vendita.prezzo_vendita != prezzo_vendita:
                auto_vendita.prezzo_vendita = prezzo_vendita
                auto_vendita.save()
        if auto_affitto is not None:
            auto_affitto.delete()
            auto_affitto = None
    if auto.disponibilita == 1:
        print('Affitto')
        if auto_affitto is None:
            auto_affitto = AutoAffitto.objects.create(auto=auto, prezzo_affitto=prezzo_affitto, affittante=auto.id_possessore)
        else:
            print("auto_affitto:", auto_affitto)
            if auto_affitto is not None and auto_affitto.prezzo_affitto != prezzo_affitto:
                auto_affitto.prezzo_affitto = prezzo_affitto
                auto_affitto.save()
        if auto_vendita is not None:
            auto_vendita.delete()
            auto_vendita = None
    if auto.disponibilita == 2:
        print('Acquisto e Affitto')
        if auto_vendita is None:
            auto_vendita = AutoVendita.objects.create(auto=auto, prezzo_vendita=prezzo_vendita, venditore=auto.id_possessore)
        else:
            if auto_vendita is not None and auto_vendita.prezzo_vendita != prezzo_vendita:
                auto_vendita.prezzo_vendita = prezzo_vendita
                auto_vendita.save()
        if auto_affitto is None:
            auto_affitto = AutoAffitto.objects.create(auto=auto, prezzo_affitto=prezzo_affitto, affittante=auto.id_possessore)
        else:
            print("auto_affitto:", auto_affitto)
            if auto_affitto is not None and auto_affitto.prezzo_affitto != prezzo_affitto:
                auto_affitto.prezzo_affitto = prezzo_affitto
                auto_affitto.save()
    auto.save()

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
