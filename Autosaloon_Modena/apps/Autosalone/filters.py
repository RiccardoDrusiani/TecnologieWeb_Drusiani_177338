import django_filters
from apps.Auto.models import Auto
from apps.utils import DISPONIBILITA_CHOICES

class AutoFilterSet(django_filters.FilterSet):
    marca = django_filters.CharFilter(lookup_expr='icontains', label='Marca')
    modello = django_filters.CharFilter(lookup_expr='icontains', label='Modello')
    anno = django_filters.NumberFilter(label='Anno')
    cilindrata = django_filters.NumberFilter(label='Cilindrata')
    carburante = django_filters.ChoiceFilter(choices=Auto._meta.get_field('carburante').choices, label='Carburante')
    cambio = django_filters.ChoiceFilter(choices=Auto._meta.get_field('cambio').choices, label='Cambio')
    trazione = django_filters.ChoiceFilter(choices=Auto._meta.get_field('trazione').choices, label='Trazione')
    disponibilita = django_filters.ChoiceFilter(choices=DISPONIBILITA_CHOICES, label='Disponibilità')
    chilometraggio = django_filters.NumberFilter(label='Chilometraggio massimo', field_name='chilometraggio', lookup_expr='lte')
    prezzo = django_filters.NumberFilter(label='Prezzo massimo', method='filter_prezzo')

    class Meta:
        model = Auto
        fields = ['marca', 'modello', 'anno', 'cilindrata', 'carburante', 'cambio', 'trazione', 'disponibilita', 'chilometraggio']

    def filter_prezzo(self, queryset, name, value):
        # Non tutte le auto hanno prezzo, quindi si filtra solo se presente
        if hasattr(queryset.model, 'prezzo'):
            return queryset.filter(prezzo__lte=value)
        return queryset

