from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, DetailView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from .models import Message
from .forms import MessageForm
from apps.Auto.models import Auto
from django.db.models import Q
import django_filters
from django.contrib.auth.models import Group
from apps.utils import DISPONIBILITA_CHOICES
from .filters import AutoFilterSet

# Create your views here.
def home(request):
    """
    Render the home page of the Autosalone application.
    """
    cars = Auto.objects.all()
    filterset = AutoFilterSet(request.GET, queryset=cars)
    paginator = Paginator(filterset.qs, 9)
    page_number = request.GET.get('page')
    cars_page = paginator.get_page(page_number)

    # Determina se l'utente appartiene a un gruppo specifico
    is_concessionaria = request.user.groups.filter(name='concessionaria').exists() if request.user.is_authenticated else False
    is_user = request.user.groups.filter(name='utente').exists() if request.user.is_authenticated else False

    return render(request, 'Autosalone/home.html', {
        'cars_page': cars_page,
        'filter': filterset,
        'is_concessionaria': is_concessionaria,
        'is_user': is_user,
        'disponibilita_choices': DISPONIBILITA_CHOICES,
    })

class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'Autosalone/message_form.html'
    success_url = reverse_lazy('message-list')

    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super().form_valid(form)

class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'Autosalone/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        user = self.request.user
        user_ct = ContentType.objects.get_for_model(user.__class__)
        return Message.objects.filter(receiver_content_type=user_ct, receiver_object_id=user.pk)

class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'Autosalone/message_detail.html'
    context_object_name = 'message'

class AutoFilter:
    def __init__(self, data):
        self.data = data
        self.disponibilita_choices = DISPONIBILITA_CHOICES

    def filter(self, queryset):
        marca = self.data.get('marca')
        modello = self.data.get('modello')
        anno = self.data.get('anno')
        cilindrata = self.data.get('cilindrata')
        carburante = self.data.get('carburante')
        cambio = self.data.get('cambio')
        trazione = self.data.get('trazione')
        disponibilita = self.data.get('disponibilita')
        prezzo = self.data.get('prezzo')

        if marca:
            queryset = queryset.filter(marca__icontains=marca)
        if modello:
            queryset = queryset.filter(modello__icontains=modello)
        if anno:
            queryset = queryset.filter(anno=anno)
        if cilindrata:
            queryset = queryset.filter(cilindrata=cilindrata)
        if carburante != '' and carburante is not None:
            queryset = queryset.filter(carburante=carburante)
        if cambio != '' and cambio is not None:
            queryset = queryset.filter(cambio=cambio)
        if trazione != '' and trazione is not None:
            queryset = queryset.filter(trazione=trazione)
        if disponibilita and disponibilita in dict(DISPONIBILITA_CHOICES):
            queryset = queryset.filter(disponibilita=disponibilita)
        if prezzo:
            queryset = queryset.filter(prezzo__lte=prezzo)
        return queryset

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
        if hasattr(queryset.model, 'prezzo'):
            return queryset.filter(prezzo__lte=value)
        return queryset
