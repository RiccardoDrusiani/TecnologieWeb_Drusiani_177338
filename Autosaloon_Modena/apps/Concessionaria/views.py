from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .mixin import ConcessionariaRequiredMixin
from .models import Concessionaria, HistoryVendute, HistoryAffittate
from .form import ConcessionariaUpdateForm, ConcessionariaCreateForm, ConcessionariaFullUpdateForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse

from ..Auto.models import Auto, AutoContrattazione, AutoAffitto, AutoPrenotazione
from ..Chat.models import ChatRoom
from ..utils import user_or_concessionaria
from ..Autosalone.filters import AutoFilterSet


class ConcessionariaCreateView(CreateView):
    model = User
    form_class = ConcessionariaCreateForm
    template_name = 'Concessionaria/registration_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save(commit=False)
        # Creazione dell'utente e della concessionaria
        user.set_password(form.cleaned_data['password'])
        user = form.save()
        group, created = Group.objects.get_or_create(name='concessionaria')
        user.groups.add(group)
        Concessionaria.objects.create(
            user=user,
            partita_iva = form.cleaned_data['partita_iva'],
            codice_fiscale = form.cleaned_data['codice_fiscale']
        )
        # Autenticazione e login automatico dopo la registrazione
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'], email=form.cleaned_data['email'])
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Errore durante la registrazione. Controlla i dati inseriti.")
        return super().form_invalid(form)

class ConcessionariaUpdateView(ConcessionariaRequiredMixin, UpdateView):
    model = Concessionaria
    form_class = ConcessionariaUpdateForm
    template_name = 'Concessionaria/concessionaria_form.html'
    success_url = reverse_lazy('home')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

class ConcessionariaDeleteView(ConcessionariaRequiredMixin, DeleteView):
    model = Concessionaria
    template_name = 'Concessionaria/concessionaria_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('home')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.object.user
        Auto.objects.filter(user_auto=user).delete()
        user.delete()
        logout(request)
        request.session.flush()
        return redirect(self.success_url)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.success_url

class ConcessionariaLoginView(LoginView):
    # ...existing code...
    def form_valid(self, form):
        user = form.get_user()
        if user.groups.filter(name='concessionaria').exists():
            login(self.request, user)
            return redirect('home')
        else:
            messages.error(self.request, "Accesso riservato alle concessionarie.")
            return redirect('concessionaria-login')

    def form_invalid(self, form):
        messages.error(self.request, "Email o password non validi.")
        return redirect('concessionaria-login')

@login_required
def impostazioni_concessionaria(request):
    try:
        concessionaria_profile = request.user.concessionaria_profile
        if not request.user.groups.filter(name="concessionaria").exists():
            messages.error(request, "Accesso riservato alle concessionarie.")
            return HttpResponseRedirect(reverse('home'))
    except Concessionaria.DoesNotExist:
        concessionaria_profile = Concessionaria.objects.create(user=request.user)
        concessionaria_profile.save()  # Forza la generazione dello slug
    # Se per qualche motivo lo slug non è stato generato, forzalo ora
    if not concessionaria_profile.slug:
        concessionaria_profile.save()
    if request.method == 'POST':
        form = ConcessionariaFullUpdateForm(request.POST, instance=concessionaria_profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dati aggiornati correttamente!')
            return redirect('Concessionaria:impostazioni_concessionaria')
        else:
            messages.error(request, 'Errore nell\'aggiornamento dei dati. Controlla i campi.')
    else:
        form = ConcessionariaFullUpdateForm(instance=concessionaria_profile, user=request.user)
    return render(request, 'Concessionaria/impostazioni_concessionaria_template.html', {
        'user': request.user,
        'concessionaria_profile': concessionaria_profile,
        'form': form,
    })



class ContrattazioniView(LoginRequiredMixin, View):
    def get(self, request):
        tipologia, id = user_or_concessionaria(self.request.user)
        contrattazioni_avviate = AutoContrattazione.objects.filter(
            acquirente_id=id,
            acquirente_tipologia=tipologia
        )
        list_auto_contr_iniziato = []
        chat_ids_avviate = {}
        for contrattazione in contrattazioni_avviate:
            auto = Auto.objects.get(id=contrattazione.auto.id)
            list_auto_contr_iniziato.append(auto)
            venditore = auto.user_auto
            acquirente = request.user
            chat = ChatRoom.objects.filter(
                Q(user_1=acquirente, user_2=venditore) | Q(user_1=venditore, user_2=acquirente),
                auto_chat=auto
            ).first()
            chat_ids_avviate[contrattazione.id] = chat.id if chat else None

        contrattazioni_ricevute = AutoContrattazione.objects.filter(
            venditore_id=id,
            venditore_tipologia=tipologia
        )
        list_auto_contr_ricevuto = []
        chat_ids_ricevute = {}
        for contrattazione in contrattazioni_ricevute:
            auto = Auto.objects.get(id=contrattazione.auto.id)
            list_auto_contr_ricevuto.append(auto)
            venditore = request.user
            try:
                acquirente = User.objects.get(id=contrattazione.acquirente_id)
            except User.DoesNotExist:
                acquirente = None
            if acquirente:
                chat = ChatRoom.objects.filter(
                    Q(user_1=acquirente, user_2=venditore) | Q(user_1=venditore, user_2=acquirente),
                    auto_chat=auto
                ).first()
                chat_ids_ricevute[contrattazione.id] = chat.id if chat else None
            else:
                chat_ids_ricevute[contrattazione.id] = None

        # Applica filtro solo alle auto coinvolte nelle contrattazioni
        all_auto = list_auto_contr_iniziato + list_auto_contr_ricevuto
        auto_qs = Auto.objects.filter(id__in=[a.id for a in all_auto])
        filterset = AutoFilterSet(request.GET, queryset=auto_qs.distinct())
        filtered_auto_ids = set(a.id for a in filterset.qs)
        # Filtra le due liste
        list_auto_contr_iniziato = [a for a in list_auto_contr_iniziato if a.id in filtered_auto_ids]
        list_auto_contr_ricevuto = [a for a in list_auto_contr_ricevuto if a.id in filtered_auto_ids]
        # Filtra anche le contrattazioni mostrate
        contrattazioni_avviate = [c for c in contrattazioni_avviate if c.auto.id in filtered_auto_ids]
        contrattazioni_ricevute = [c for c in contrattazioni_ricevute if c.auto.id in filtered_auto_ids]

        return render(request, 'Concessionaria/contrattazioni.html', {
            'contrattazioni_avviate': contrattazioni_avviate,
            'contrattazioni_ricevute': contrattazioni_ricevute,
            'list_auto_contr_iniziato': list_auto_contr_iniziato,
            'list_auto_contr_ricevuto': list_auto_contr_ricevuto,
            'chat_ids_avviate': chat_ids_avviate,
            'chat_ids_ricevute': chat_ids_ricevute,
            'filter': filterset,
        })

class AutoVenduteView(ConcessionariaRequiredMixin, LoginRequiredMixin, View):
    def get(self, request):
        # Recupera la concessionaria associata all'utente loggato
        concessionaria = getattr(self.request.user, 'concessionaria_profile', None)
        if concessionaria:
            auto_vendute = HistoryVendute.objects.filter(concessionaria=concessionaria.user)
        else:
            auto_vendute = HistoryVendute.objects.none()
        print(auto_vendute)
        # filterset = AutoFilterSet(request.GET, queryset=Auto.objects.all())
        return render(request, 'Concessionaria/auto_vendute.html', {
            'auto_vendute': auto_vendute,
            # 'filter': filterset,
        })

class AutoAffittateView(ConcessionariaRequiredMixin, LoginRequiredMixin, View):
    def get(self, request):
        # Filtro solo auto affittate (disponibilita = 'affittata')
        concessionaria = getattr(self.request.user, 'concessionaria_profile', None)
        if concessionaria:
            auto_affittate = HistoryAffittate.objects.filter(concessionaria=concessionaria.user)
        else:
            auto_affittate = HistoryAffittate.objects.none()
        # filterset = AutoFilterSet(request.GET, queryset=Auto.objects.all())
        return render(request, 'Concessionaria/auto_affittate.html', {
            'auto_affittate': auto_affittate,
            # 'filter': filterset,
        })

class AnnullaAffittoView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        try:
            affitto = AutoAffitto.objects.get(pk=pk)
        except AutoAffitto.DoesNotExist:
            messages.error(request, "Affitto non trovato.")
            return HttpResponseRedirect(reverse('Concessionaria:auto_affittate'))

        now = timezone.now()
        # Se l'affitto è attivo (affittata=True e oggi tra data_inizio e data_fine)
        if affitto.affittata and affitto.data_inizio and affitto.data_fine and affitto.data_inizio <= now <= affitto.data_fine:
            affitto.data_inizio = None
            affitto.data_fine = None
            affitto.affittata = False
            affitto.save()
            messages.success(request, "Affitto attivo annullato e rimosso con successo.")
        else:
            lista_affitto = HistoryAffittate.objects.filter(auto=affitto.auto, affittante=id).order_by('-data_fine')
            messages.success(request, "Affitto rimosso con successo.")
        return HttpResponseRedirect(reverse('Concessionaria:auto_affittate'))

class AutoAffittiPrenotazioniView(ConcessionariaRequiredMixin, LoginRequiredMixin, View):
    def get(self, request):
        concessionaria = getattr(request.user, 'concessionaria_profile', None)
        auto_list = []
        if not concessionaria:
            return render(request, 'Concessionaria/auto_affitti_prenotazioni.html', {'auto_list': []})

        # Filtri
        marca = request.GET.get('marca', '').strip()
        modello = request.GET.get('modello', '').strip()
        anno = request.GET.get('anno', '').strip()
        stato = request.GET.get('stato', 'tutte')

        # Recupera affitti
        affitti = AutoAffitto.objects.filter(affittante=concessionaria.user.id, affittata=True)
        prenotazioni = AutoPrenotazione.objects.filter(proprietario_id=concessionaria.user.id, prenotata=True)

        # Applica filtri
        if marca:
            affitti = affitti.filter(auto__marca__icontains=marca)
            prenotazioni = prenotazioni.filter(auto__marca__icontains=marca)
        if modello:
            affitti = affitti.filter(auto__modello__icontains=modello)
            prenotazioni = prenotazioni.filter(auto__modello__icontains=modello)
        if anno:
            affitti = affitti.filter(auto__anno=anno)
            prenotazioni = prenotazioni.filter(auto__anno=anno)

        auto_list = []
        if stato == 'affittate' or stato == 'tutte':
            for aff in affitti:
                auto_list.append({
                    'auto': aff.auto,
                    'stato': 'Affittata',
                    'data_inizio': aff.data_inizio,
                    'data_fine': aff.data_fine
                })
        if stato == 'prenotate' or stato == 'tutte':
            for pren in prenotazioni:
                auto_list.append({
                    'auto': pren.auto,
                    'stato': 'Prenotata',
                    'data_inizio': pren.data_inizio,
                    'data_fine': pren.data_fine
                })
        # Ordina per data_inizio decrescente
        auto_list.sort(key=lambda x: x['data_inizio'] or '', reverse=True)
        return render(request, 'Concessionaria/auto_affitti_prenotazioni.html', {'auto_list': auto_list})
