from datetime import timezone, datetime, timedelta

from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .auto_utils import gestione_vendita_affitto, check_affittata_in_periodo
from .form import AddAutoForm, ModifyAutoForm, AffittoAutoForm, PrenotazioneAutoForm, VenditaAutoForm, \
    ContrattoAutoForm, AffittoAutoListaForm
from .mixin import UserIsOwnerMixin
from .models import Auto, AutoAffitto, AutoVendita, AutoPrenotazione, AutoContrattazione, TIPOLOGIE_CARBURANTE, \
    TIPOLOGIE_TRAZIONE, DISPONIBILITA, AutoListaAffitto, ContrattazioneOfferta
from ..Concessionaria.models import HistoryAffittate, HistoryVendute
from ..Utente.models import UserExtendModel
from ..decorator import user_or_concessionaria_required
from ..utils import user_or_concessionaria, get_success_url_by_possessore, is_possessore_auto
from ..Chat.models import ChatRoom


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
class AutoAffittoView(CreateView):
    model = AutoListaAffitto
    form_class = AffittoAutoListaForm
    template_name = 'Auto/affitto_auto.html'

    def form_valid(self, form):
        auto_id = self.kwargs.get('pk')
        auto = Auto.objects.get(pk=auto_id)
        chat = ChatRoom.objects.get_or_create(
            name=f"Affitto Auto: {auto.marca} {auto.modello}",
            auto_chat=auto,
            user_1=auto.user_auto,
            user_2=self.request.user
        )
        affitto = AutoAffitto.objects.filter(auto=auto).first()
        lista_affitto = form.save(commit=False)
        print("Affitto auto:", affitto)

        lista_affitto.lista_auto_affitto=affitto
        lista_affitto.data_pubblicazione=datetime.now()
        lista_affitto.prezzo_affitto=affitto.prezzo_affitto
        lista_affitto.affittante = self.request.user.id
        lista_affitto.affittante_tipologia = self.request.user.groups.first().name
        lista_affitto.data_inizio = form.cleaned_data.get('data_inizio')
        lista_affitto.data_fine = form.cleaned_data.get('data_fine')
        auto.save()

        if auto.user_auto.groups.filter(name="concessionaria").exists():
            HistoryAffittate.objects.create(
                concessionaria=auto.user_auto,
                auto_id = auto.id,
                affittante_username=self.request.user.username,
                auto_marca=auto.marca,
                auto_modello=auto.modello,
                data_inizio=lista_affitto.data_inizio,
                data_fine=lista_affitto.data_fine,
                prezzo_affitto=lista_affitto.prezzo_affitto
            )

        lista_affitto.save()
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
        if auto.user_auto.groups.filter(name="concessionaria").exists():
            HistoryVendute.objects.create(
                concessionaria=auto.user_auto,
                auto_id =auto.id,
                acquirente_username=self.request.user.username,
                auto_marca=auto.marca,
                auto_modello=auto.modello,
                data=datetime.now(),
                prezzo_vendita=vendita.prezzo_vendita if vendita else 0
            )
        if auto.disponibilita != [5, 7]:
            chat = ChatRoom.objects.get_or_create(
                name=f"Acquisto Auto: {auto.marca} {auto.modello}",
                auto_chat=auto,
                user_1=auto.user_auto,
                user_2=self.request.user
            )
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

            if vendita:
                vendita.save()
            # Elimina la prenotazione se esiste
            auto_prenotata = AutoPrenotazione.objects.filter(auto=auto)
            if auto_prenotata.exists():
                auto_prenotata.delete()
                auto.disponibilita = auto.disponibilita_prec
                auto.disponibilita_prec = 8  # Imposta la disponibilità a "Vendita"
            # Elimina la contrattazione se esiste
            auto_contrattazione = AutoContrattazione.objects.filter(auto=auto)
            if auto_contrattazione.exists():
                auto_contrattazione.delete()
                auto.disponibilita = auto.disponibilita_prec
                auto.disponibilita = 8  # Imposta la disponibilità a "Vendita"

            auto.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form, errore="L'auto è già in vendita o affitto.")

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
        user = self.request.user
        from django.utils import timezone
        if user.groups.filter(name='utente').exists():
            extend_user = UserExtendModel.objects.get(user=user)
            # Consenti la prenotazione solo se il blocco è assente o scaduto
            if extend_user.data_fine_blocco_prenotazioni is None or extend_user.data_fine_blocco_prenotazioni < timezone.now():
                auto = Auto.objects.get(id=self.kwargs['pk'])
                if auto.disponibilita not in [0, 1, 2, 8]:
                    print("Disponibilita non valida")
                    return self.form_invalid(form, disponibilita=True)
                auto.disponibilita_prec = auto.disponibilita
                auto.disponibilita = 6  # Imposta la disponibilità a "Pren
                auto.save()
                prenotazione.auto = auto
                prenotazione.prenotata = True
                data_inizio = timezone.now()
                prenotazione.data_inizio = data_inizio
                prenotazione.data_fine = data_inizio + timedelta(hours=24)
                prenotazione.data_pubblicazione = timezone.now()
                prenotazione.proprietario_id = auto.id_possessore
                prenotazione.proprietario_tipologia = auto.tipologia_possessore
                prenotazione.prenotante_tipologia, prenotazione.prenotante_id = user_or_concessionaria(self.request.user)
                prenotazione.save()
                # Blocca le prenotazioni per 24 ore
                extend_user.data_inizio_blocco_prenotazioni = timezone.now()
                extend_user.data_fine_blocco_prenotazioni = extend_user.data_inizio_blocco_prenotazioni + timedelta(hours=24)
                extend_user.save()
                chat = ChatRoom.objects.get_or_create(
                    name=f"Prenotazione Auto: {auto.marca} {auto.modello}",
                    auto_chat=auto,
                    user_1=auto.user_auto,
                    user_2=self.request.user
                )
                return super().form_valid(form)
            else:
                # Blocco attivo, mostra errore
                return self.form_invalid(form, blocco_attivo=True)
        # Non è un utente, mostra errore
        return self.form_invalid(form, non_utente=True)


    def form_invalid(self, form, blocco_attivo=False, non_utente=False, disponibilita=False):
        context = {'form': form}
        if blocco_attivo:
            context['errore_blocco'] = "Non puoi prenotare: hai un blocco attivo sulle prenotazioni."
        if non_utente:
            context['errore_non_utente'] = "Solo gli utenti possono prenotare."
        if disponibilita:
            context['errore_disponibilita'] = "L'auto non è disponibile per la prenotazione."
        return render(self.request, self.template_name, context)

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        auto = Auto.objects.get(pk=self.kwargs['pk'])
        from django.utils import timezone
        data_inizio = timezone.now()
        data_fine = data_inizio + timedelta(hours=24)
        context['auto'] = auto
        context['data_inizio'] = data_inizio.strftime('%d/%m/%Y %H:%M')
        context['data_fine'] = data_fine.strftime('%d/%m/%Y %H:%M')
        return context



@method_decorator(login_required, name='dispatch')
class AutoInContrattazioneView(CreateView):
    model = AutoContrattazione
    template_name = 'Auto/contrattazione_auto.html'
    form_class = ContrattoAutoForm

    def form_valid(self, form):
        print("Form validato con successo")
        contrattazione = form.save(commit=False)
        auto = Auto.objects.get(id=self.kwargs['pk'])
        auto_vendita = AutoVendita.objects.filter(auto=auto).first()
        contrattazione.auto = auto

        if contrattazione.stato == 0:
            contrattazione.venditore_tipologia, contrattazione.venditore_id = auto.tipologia_possessore, auto.id_possessore
            contrattazione.acquirente_tipologia, contrattazione.acquirente_id = user_or_concessionaria(self.request.user)
            contrattazione.prezzo_iniziale = auto_vendita.prezzo_vendita
            contrattazione.data_inizio = datetime.now(timezone.utc)
            contrattazione.stato = 1  # Venditore in contrattazione
            auto.disponibilita_prec = auto.disponibilita
            auto.disponibilita = 5  # Imposta la disponibilità a "In Contrattazione"
            auto.save()
            chat = ChatRoom.objects.get_or_create(
                name=f"Contrattazione Auto: {auto.marca} {auto.modello}",
                auto_chat=auto,
                user_1=auto.user_auto,
                user_2=self.request.user
            )
        elif contrattazione.stato == 1:
            contrattazione.stato = 2  # Acquirente in contrattazione
        elif contrattazione.stato == 2:
            contrattazione.stato = 1

        contrattazione.prezzo_iniziale = form.cleaned_data.get('prezzo_attuale')
        contrattazione.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

    def get_success_url(self):
        from django.urls import reverse
        return reverse('Concessionaria:contrattazioni')

class ContrattazioneOffertaView(UpdateView):
    model = AutoContrattazione
    template_name = 'Auto/contrattazione_auto.html'
    form_class = ContrattoAutoForm

    def form_valid(self, form):
        contrattazione = form.save(commit=False)
        print("Form validato con successo")
        contrattazione.prezzo_attuale = form.cleaned_data.get('prezzo_attuale')
        if contrattazione.stato == 1:
            contrattazione.stato = 2  # Acquirente in contrattazione
        elif contrattazione.stato == 2:
            contrattazione.stato = 1
        contrattazione.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form non valido")
        return render(self.request, self.template_name, {'form': form})

    def get_success_url(self):
        from django.urls import reverse
        if self.request.user.groups.filter(name='concessionaria').exists():
            return reverse('Concessionaria:contrattazioni')
        else:
            return reverse('Utente:gestione_auto')

@method_decorator(login_required, name='dispatch')
class AutoFineContrattazioneFallitaView(UpdateView):
    model = AutoContrattazione
    def post(self, request, pk, *args, **kwargs):
        contrattazione = get_object_or_404(AutoContrattazione, pk=pk)
        auto = contrattazione.auto
        # Riporta la disponibilità allo stato precedente
        auto.disponibilita = auto.disponibilita_prec
        auto.save()
        # Elimina la contrattazione
        contrattazione.delete()
        # Redirect
        from django.urls import reverse
        if request.user.groups.filter(name='concessionaria').exists():
            return redirect(reverse('Concessionaria:contrattazioni'))
        else:
            return redirect(reverse('Utente:gestione_auto'))

@method_decorator(login_required, name='dispatch')
class AutoFineContrattazioneSuccessoView(UpdateView):
    model = AutoContrattazione

    def post(self, request, pk, *args, **kwargs):
        contrattazione = get_object_or_404(AutoContrattazione, pk=pk)
        auto = contrattazione.auto
        # Cambia possessore auto
        auto.user_auto_id = contrattazione.acquirente_id
        auto.tipologia_possessore = contrattazione.acquirente_tipologia
        auto.id_possessore = contrattazione.acquirente_id
        # Riporta la disponibilità allo stato precedente
        auto.disponibilita = auto.disponibilita_prec
        auto.save()
        # Aggiorna AutoVendita
        vendita = AutoVendita.objects.filter(auto=auto).first()
        if vendita:
            vendita.venditore = contrattazione.acquirente_id
            vendita.save()
        # Aggiorna AutoAffitto
        affitto = AutoAffitto.objects.filter(auto=auto).first()
        if affitto:
            affitto.affittante = contrattazione.acquirente_id
            affitto.affittuario = None
            affitto.affittuario_tipologia = None
            affitto.save()
        # Elimina la contrattazione
        contrattazione.delete()
        # Redirect
        from django.urls import reverse
        if request.user.groups.filter(name='concessionaria').exists():
            return redirect(reverse('Concessionaria:contrattazioni'))
        else:
            return redirect(reverse('Utente:gestione_auto'))




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
    auto_affitto = AutoAffitto.objects.filter(auto=auto).first()
    if is_possessore_auto(request.user, auto):
        return HttpResponseForbidden("Non hai i permessi per affittare questa auto.")

    data_inizio = request.POST.get('data_inizio') or request.GET.get('data_inizio')
    data_fine = request.POST.get('data_fine') or request.GET.get('data_fine')
    errore_date = None

    # Controllo validità date
    if data_inizio and data_fine:
        try:
            print("data_inizio:", data_inizio)
            print("data_fine:", data_fine)
            data_inizio_dt = datetime.strptime(data_inizio, "%Y-%m-%d")
            data_fine_dt = datetime.strptime(data_fine, "%Y-%m-%d")
            if data_fine_dt < data_inizio_dt:
                errore_date = "La data di fine non può essere precedente alla data di inizio."
            if check_affittata_in_periodo(auto_affitto, data_inizio, data_fine):
                errore_date = "L'auto è già affittata in questo periodo."
        except Exception:
            errore_date = "Formato data non valido."

    if errore_date:
        return HttpResponseForbidden(f"Errore: {errore_date}")

    return render(request, 'Auto/affitta_auto.html', {
        'object': auto,
        'data_inizio': data_inizio,
        'data_fine': data_fine,
    })

@login_required
def ContattazioneAutoView(request, pk):
    auto = get_object_or_404(Auto, pk=pk)
    auto_contrattazione = AutoContrattazione.objects.filter(auto=auto).first()
    if auto_contrattazione == None:
        auto_contrattazione = None
    auto_vendita = AutoVendita.objects.filter(auto=auto).first()

    return render(request, 'Auto/contrattazione_auto.html', {
        'auto': auto,
        'prezzo_vendita_auto_iniziale': auto_vendita.prezzo_vendita,
        'contrattazione': auto_contrattazione,
    })
