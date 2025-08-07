from datetime import timezone, datetime, timedelta

from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .auto_utils import gestione_vendita_affitto
from .form import AddAutoForm, ModifyAutoForm, AffittoAutoForm, PrenotazioneAutoForm, VenditaAutoForm, ContrattoAutoForm
from .mixin import UserIsOwnerMixin
from .models import Auto, AutoAffitto, AutoVendita, AutoPrenotazione, AutoContrattazione, TIPOLOGIE_CARBURANTE, TIPOLOGIE_TRAZIONE, DISPONIBILITA
from ..decorator import user_or_concessionaria_required
from ..utils import user_or_concessionaria, get_success_url_by_possessore, is_possessore_auto



@method_decorator(login_required, name='dispatch')
class AutoAddView(CreateView):
    model = Auto
    template_name = 'Auto/add_auto_template.html'  # Cambiato il template
    form_class = AddAutoForm

    def form_valid(self, form):
        auto = form.save(commit=False)
        auto.tipologia_possessore, auto.id_possessore = user_or_concessionaria(self.request.user)
        auto.user_auto = self.request.user  # Associa l'utente autenticato
        auto.save()
        prezzo_vendita = form.cleaned_data.get('prezzo_vendita')
        prezzo_affitto = form.cleaned_data.get('prezzo_affitto')
        if prezzo_vendita:
            AutoVendita.objects.create(auto=auto, prezzo_vendita=prezzo_vendita, venditore=auto.id_possessore)
        if prezzo_affitto:
            AutoAffitto.objects.create(auto=auto, prezzo_affitto=prezzo_affitto, affittante=auto.id_possessore)
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)


@method_decorator(login_required, name='dispatch')
class AutoDeleteView(UserIsOwnerMixin, DeleteView):
    model = Auto
    template_name = 'Autosalone/confirm_delete_popup.html'

    def delete(self, request, *args, **kwargs):
        auto = self.get_object()
        # Elimina le istanze collegate in AutoVendita e AutoAffitto
        AutoVendita.objects.filter(auto=auto).delete()
        AutoAffitto.objects.filter(auto=auto).delete()
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)



@method_decorator(login_required, name='dispatch')
class AutoModifyView(UserIsOwnerMixin, UpdateView):
    model = Auto
    template_name = 'Auto/modify_auto.html'
    form_class = ModifyAutoForm

    def get_initial(self):
        initial = super().get_initial()
        auto = self.get_object()
        vendita = AutoVendita.objects.filter(auto=auto).first()
        affitto = AutoAffitto.objects.filter(auto=auto).first()
        # Imposta la disponibilità in base a cosa esiste
        if vendita and affitto:
            initial['disponibilita'] = '2'  # Vendita e Affitto
        elif vendita:
            initial['disponibilita'] = '0'  # Solo Vendita
        elif affitto:
            initial['disponibilita'] = '1'  # Solo Affitto
        if vendita:
            initial['prezzo_vendita'] = vendita.prezzo_vendita
        if affitto:
            initial['prezzo_affitto'] = affitto.prezzo_affitto
        return initial

    def form_valid(self, form):
        auto = form.save(commit=False)
        auto.tipologia_possessore, auto.id_possessore = user_or_concessionaria(self.request.user)
        auto.save()
        # Recupera i valori originali
        original_auto = Auto.objects.get(pk=auto.id)
        original_vendita = AutoVendita.objects.filter(auto=original_auto).first() or None
        original_affitto = AutoAffitto.objects.filter(auto=original_auto).first() or None
        # Nuovi valori dal form
        prezzo_vendita = form.cleaned_data.get('prezzo_vendita')
        prezzo_affitto = form.cleaned_data.get('prezzo_affitto')
        # Gestione della logica di vendita e affitto
        gestione_vendita_affitto(prezzo_vendita, prezzo_affitto, original_auto, original_vendita, original_affitto)
        return super().form_valid(form)


    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form, 'auto': self.get_object()})

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)



@method_decorator(login_required, name='dispatch')
class AutoAffittoView(UpdateView):
    model = Auto
    form_class = AffittoAutoForm
    template_name = 'Auto/affitto_auto.html'

    def form_valid(self, form):
        auto = form.save(commit=False)
        auto.disponibilita = '7'  # Imposta l'auto come disponibile per affitto
        affitto = AutoAffitto.objects.filter(auto_id=auto.id).first()

        affitto.affittante = self.request.user.id
        affitto.affittata = True
        affitto.data_pubblicazione = datetime.now()
        affitto.data_inizio = form.cleaned_data.get('data_inizio')
        affitto.data_fine = form.cleaned_data.get('data_fine')

        affitto.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form, 'auto': self.get_object()})

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)



@method_decorator(login_required, name='dispatch')
class AutoAcquistoView(UpdateView):
    model = Auto
    form_class = VenditaAutoForm  # Assuming the same form is used for both
    template_name = 'Auto/acquisto_auto.html'

    def form_valid(self, form):
        auto = form.save(commit=False)
        vendita = AutoVendita.objects.filter(auto=auto).first()
        if vendita:
            vendita.venditore = self.request.user.id
            vendita.data_pubblicazione = datetime.now()
        auto.tipologia_possessore, auto.id_possessore = user_or_concessionaria(self.request.user)
        print(auto.id_possessore, auto.tipologia_possessore)
        auto.user_auto_id = self.request.user.id  # Associa l'utente autenticato
        auto_affitto = AutoAffitto.objects.filter(auto_id=auto.id).first()
        if auto_affitto:
            auto_affitto.affittuario_tipologia, auto_affitto.affittuario = user_or_concessionaria(self.request.user)
            auto_affitto.affittante = None
            auto_affitto.save()
        auto.save()
        if vendita:
            vendita.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)



@method_decorator(login_required, name='dispatch')
class AutoPrenotaView(CreateView):
    model = AutoPrenotazione
    template_name = 'Auto/prenota_auto.html'
    form_class = PrenotazioneAutoForm

    def form_valid(self, form):
        prenotazione = form.save(commit=False)
        auto = Auto.objects.get(pk=self.kwargs['pk'])
        prenotazione.auto = auto
        prenotazione.data_inizio = datetime.now()
        prenotazione.data_fine = prenotazione.data_inizio + timedelta(hours=24)
        prenotazione.proprietario = auto.id_possessore
        prenotazione.prenotante_id, prenotazione.prenotante_tipologia = user_or_concessionaria(self.request.user)
        prenotazione.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)



@method_decorator(login_required, name='dispatch')
class AutoInContrattazioneView(UpdateView):
    model = AutoContrattazione
    template_name = 'Auto/contrattazione_auto.html'
    form_class = ContrattoAutoForm

    def form_valid(self, form):
        contrattazione = form.save(commit=False)
        auto = Auto.objects.get(pk=self.kwargs['pk'])
        contrattazione.auto = auto
        contrattazione.acquirente_id, contrattazione.acquirente_tipologia = user_or_concessionaria(self.request.user)
        autovendita = AutoVendita.objects.filter(auto=auto).first()
        if autovendita:
            contrattazione.prezzo_iniziale = autovendita.prezzo_vendita
        contrattazione.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)



@method_decorator(login_required, name='dispatch')
class AutoFineContrattazioneView(UpdateView):
    model = AutoContrattazione
    template_name = 'Auto/fine_contrattazione_auto.html'
    form_class = ContrattoAutoForm

    def form_valid(self, form):
        contrattazione = form.save(commit=False)
        contrattazione.prezzo_finale = contrattazione.prezzo_attuale
        contrattazione.data_fine = datetime.now(timezone.utc)
        contrattazione.save()

        # Trasferimento proprietà auto
        auto = contrattazione.auto
        auto.tipologia_possessore = contrattazione.acquirente_tipologia
        auto.id_possessore = contrattazione.acquirente_id
        auto_affitto = AutoAffitto.objects.filter(auto=auto).first()
        if auto_affitto:
            auto_affitto.affittante_id, auto_affitto.affittante_tipologia = None, None
            auto_affitto.affittuario_id, auto_affitto.affittuario_tipologia = contrattazione.acquirente_id, contrattazione.acquirente_tipologia
            auto_affitto.save()
        auto_vendita = AutoVendita.objects.filter(auto=auto).first()
        if auto_vendita:
            auto_vendita.venditore = contrattazione.venditore_id
            auto_vendita.save()
        auto.save()
        # Rimuovi l'auto dalle vendite
        AutoVendita.objects.filter(auto=auto).delete()

        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)

class AutoDetailView(DetailView):
    model = Auto
    template_name = 'Auto/auto_detail.html'
    context_object_name = 'auto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_utente'] = False
        if user.is_authenticated:
            try:
                context['is_utente'] = user.groups.filter(name="utente").exists()
            except Exception:
                context['is_utente'] = False
        # Aggiunta variabile per disponibilità
        DISPONIBILITA_CODES = [0, 1, 2, 8]  # Sostituisci con i codici che vuoi considerare
        context['is_in_disponibilita'] = self.object.disponibilita in DISPONIBILITA_CODES
        return context


@login_required
def user_autos_view(request):
    autos = Auto.objects.filter(user_auto=request.user)
    # Filtri da GET
    marca = request.GET.get('marca', '').strip()
    modello = request.GET.get('modello', '').strip()
    anno = request.GET.get('anno', '').strip()
    chilometri = request.GET.get('chilometri', '').strip()
    cilindrata = request.GET.get('cilindrata', '').strip()
    carburante = request.GET.get('carburante', '').strip()
    trazione = request.GET.get('trazione', '').strip()
    disponibilita = request.GET.get('disponibilita', '').strip()

    if marca:
        autos = autos.filter(marca__icontains=marca)
    if modello:
        autos = autos.filter(modello__icontains=modello)
    if anno:
        autos = autos.filter(anno=anno)
    if chilometri:
        autos = autos.filter(chilometraggio=chilometri)
    if cilindrata:
        autos = autos.filter(cilindrata=cilindrata)
    if carburante:
        autos = autos.filter(carburante=carburante)
    if trazione:
        autos = autos.filter(trazione=trazione)
    if disponibilita:
        autos = autos.filter(disponibilita=disponibilita)

    paginator = Paginator(autos, 9)  # 9 auto per pagina
    page_number = request.GET.get('page')
    autos_page = paginator.get_page(page_number)
    is_utente = request.user.groups.filter(name='utente').exists()
    is_concessionaria = request.user.groups.filter(name='concessionaria').exists()
    form = AddAutoForm()
    return render(request, 'Auto/user_autos.html', {
        'autos': autos,
        'is_utente': is_utente,
        'is_concessionaria': is_concessionaria,
        'form': form,
        'TIPOLOGIE_CARBURANTE': TIPOLOGIE_CARBURANTE,
        'TIPOLOGIE_TRAZIONE': TIPOLOGIE_TRAZIONE,
        'DISPONIBILITA': DISPONIBILITA
    })

@login_required
def AffittaAutoRiepilogoView(request, pk):
    auto = get_object_or_404(Auto, pk=pk)
    if is_possessore_auto(request.user, auto):
        return HttpResponseForbidden("Non hai i permessi per affittare questa auto.")

    data_inizio = request.POST.get('data_inizio') or request.GET.get('data_inizio')
    data_fine = request.POST.get('data_fine') or request.GET.get('data_fine')
    errore_date = None

    # Controllo validità date
    if data_inizio and data_fine:
        try:
            data_inizio_dt = datetime.strptime(data_inizio, "%Y-%m-%d")
            data_fine_dt = datetime.strptime(data_fine, "%Y-%m-%d")
            if data_fine_dt < data_inizio_dt:
                errore_date = "La data di fine non può essere precedente alla data di inizio."
        except Exception:
            errore_date = "Formato data non valido."

    if errore_date:
        return HttpResponseForbidden(f"Errore: {errore_date}")

    return render(request, 'Auto/affitta_auto.html', {
        'object': auto,
        'data_inizio': data_inizio,
        'data_fine': data_fine,
    })
