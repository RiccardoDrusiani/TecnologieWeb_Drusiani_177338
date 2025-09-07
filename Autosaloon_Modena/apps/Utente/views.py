from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User, Group
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib import messages

from .mixin import UtenteRequiredMixin
from .models import UserExtendModel, Segnalazione, UserModelBan
from .form import UserCreateForm, UserExtendForm, UserUpdateForm, UserDeleteForm, CommentoForm, RispostaForm, SegnalazioneForm, UserFullUpdateForm
from ..Auto.models import Commento, Risposta, Auto, AutoVendita, AutoAffitto
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import timezone
from django.utils.decorators import method_decorator
from apps.Auto.models import AutoAffitto, AutoListaAffitto, AutoPrenotazione, AutoContrattazione, Auto
from .models import UserExtendModel
from ..decorator import user_is_banned
from ..Chat.models import ChatRoom
from django.db.models import Q


# Creazione utente base + profilo esteso
class UserCreateView(CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'Utente/registration_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        # Assegna l'utente al gruppo "Utente"
        group, created = Group.objects.get_or_create(name='utente')
        user.groups.add(group)

        UserExtendModel.objects.create(user=user)
        # Autenticazione e login automatico dopo la registrazione
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Errore durante la registrazione. Controlla i dati inseriti.")
        return super().form_invalid(form)

# Modifica utente base + esteso
class UserUpdateView(UtenteRequiredMixin, UpdateView):
    model = UserExtendModel
    form_class = UserFullUpdateForm
    template_name = 'Utente/update_user.html'
    success_url = reverse_lazy('home')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Profilo aggiornato correttamente.")
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Errore durante la modifica del profilo. Controlla i dati inseriti.")
        return super().form_invalid(form)

# Eliminazione utente
class UserDeleteView(UtenteRequiredMixin, DeleteView):
    model = UserExtendModel
    template_name = 'Utente/delete_user.html'
    success_url = reverse_lazy('home')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.object.user
        # Elimina tutte le auto associate all'utente
        Auto.objects.filter(user_auto=user).delete()
        # Elimina l'utente (che elimina anche UserExtendModel per on_delete=models.CASCADE)
        user.delete()
        logout(request)
        request.session.flush()
        return redirect(self.success_url)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

# Creazione commento
class CommentoCreateView(UtenteRequiredMixin, CreateView):
    model = Commento
    form_class = CommentoForm
    template_name = 'Utente/create_commento.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        auto_id = self.request.POST.get('auto_id')
        auto = None
        if auto_id:
            auto = Auto.objects.get(pk=auto_id)
        commento = form.save(commit=False)
        commento.user = self.request.user
        commento.auto = auto
        commento.save()
        return redirect(auto.get_absolute_url() if auto else self.success_url)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['testo'].widget.attrs['placeholder'] = 'Scrivi un commento...'
        return form

# Creazione risposta
class RispostaCreateView(CreateView):
    model = Risposta
    form_class = RispostaForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        commento_id = self.request.GET.get('commento_id') or self.request.POST.get('commento_id')
        commento = Commento.objects.get(pk=commento_id)
        risposta = form.save(commit=False)
        risposta.user = self.request.user
        risposta.commento = commento
        risposta.save()
        auto = commento.auto
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'testo': risposta.testo,
                'username': risposta.user.username,
                'data_creazione': risposta.data_creazione.strftime('%d/%m/%Y %H:%M'),
            })
        return redirect(auto.get_absolute_url())

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Dati non validi.'})
        return super().form_invalid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['testo'].widget.attrs['placeholder'] = 'Scrivi una risposta...'
        return form

    def get(self, request, *args, **kwargs):
        return redirect('home')

# Creazione segnalazione
@method_decorator(login_required, name='dispatch')
@method_decorator(user_is_banned, name='dispatch')
class SegnalazioneCreateView(CreateView):
    model = Segnalazione
    form_class = SegnalazioneForm
    template_name = 'Utente/conferma_segnalazione.html'
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        commento_id = request.GET.get('commento_id')
        if not commento_id:
            messages.error(request, "Segnalazione non valida: commento mancante.")
            return redirect(self.success_url)
        try:
            commento = Commento.objects.get(id=commento_id)
        except Commento.DoesNotExist:
            messages.error(request, "Commento non trovato.")
            return redirect(self.success_url)
        # Mostra una pagina di conferma con il commento da segnalare
        form = self.form_class(initial={'commento': commento})
        return render(request, self.template_name, {'form': form, 'commento': commento})

    def post(self, request, *args, **kwargs):
        commento_id = request.POST.get('commento_id')
        if not commento_id:
            messages.error(request, "Segnalazione non valida: commento mancante.")
            return redirect(self.success_url)
        try:
            commento = Commento.objects.get(id=commento_id)
            segnalato = commento.user
            if hasattr(segnalato, 'concessionaria_profile'):
                messages.error(request, "Non puoi segnalare una concessionaria.")
                return redirect(self.success_url)
            form = self.form_class(request.POST)
            if form.is_valid():
                segnalazione = form.save(commit=False)
                segnalazione.commento = commento
                segnalazione.segnalatore_id = request.user.id
                segnalazione.segnalato_id = segnalato.id
                segnalazione.data_segnalazione = timezone.now()
                segnalazione.save()
                # Incrementa il contatore di segnalazioni per l'utente segnalato
                try:
                    user_ban_profile = segnalato.user_ban_profile
                    user_ban_profile.segnalazioni += 1
                    user_ban_profile.save()
                except UserModelBan.DoesNotExist:
                    UserModelBan.objects.create(user=segnalato, segnalazioni=1, qnt_ban=0)
                messages.success(request, "Segnalazione inviata correttamente.")
                return redirect(self.success_url)
            else:
                return render(request, self.template_name, {'form': form, 'commento': commento})
        except Commento.DoesNotExist:
            messages.error(request, "Commento non trovato.")
            return redirect(self.success_url)


# View per il logout utente
class UserLogoutView(LogoutView):
    next_page = 'home'

# Login utente
class UserLoginView(LoginView):
    template_name = 'Utente/login.html'
    success_url = reverse_lazy('home')
    error_url = reverse_lazy('login')

    def form_valid(self, form):
        if self.request.user.is_authenticated and self.request.user.groups.filter(name="utente").exists():
            login(self.request, form.get_user())
            return redirect(self.success_url)
        else:
            messages.error(self.request, "Accesso riservato agli utenti.")
            return redirect(self.error_url)

    def form_invalid(self, form):
        messages.error(self.request, "Email o password non validi.")
        return redirect('login')

@login_required
def impostazioni_utente(request):
    try:
        user_profile = request.user.user_extend_profile
        if not request.user.groups.filter(name="utente").exists():
            messages.error(request, "Accesso riservato agli utenti.")
            return redirect('home')
    except UserExtendModel.DoesNotExist:
        user_profile = UserExtendModel.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserFullUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profilo aggiornato correttamente.")
            return redirect('Utente:impostazioni_utente')
        else:
            messages.error(request, "Errore durante la modifica del profilo. Controlla i dati inseriti.")
    else:
        form = UserFullUpdateForm(instance=user_profile)

    return render(request, 'Utente/impostazioni_utente_template.html', {
        'form': form,
        'user': request.user,
        'user_extend_profile': user_profile,
    })

@login_required
def gestione_auto(request):
    try:
        user = request.user
        if not request.user.groups.filter(name="utente").exists():
            messages.error(request, "Accesso riservato agli utenti.")
            return redirect('home')
    except UserExtendModel.DoesNotExist:
        user= UserExtendModel.objects.create(user=request.user)
    user_extend = UserExtendModel.objects.get(user=user)
    # Auto: tutte le auto dell'utente
    auto_list = Auto.objects.filter(user_auto=user)
    # Affitti: auto dove l'utente è possessore o affittuario
    affitti = AutoAffitto.objects.filter(affittante=user.id) | AutoAffitto.objects.filter(affittuario=user.id)
    affitti = affitti.select_related('auto')
    affitti_info = []
    for affitto in affitti:
        affittante_nome = affitto.affittante if not hasattr(affitto, 'affittante') or not affitto.affittante else User.objects.filter(id=affitto.affittante).first()
        affittuario_nome = affitto.affittuario if not hasattr(affitto, 'affittuario') or not affitto.affittuario else User.objects.filter(id=affitto.affittuario).first()
        affitti_info.append({
            'affitto': affitto,
            'affittante_nome': affittante_nome.username if affittante_nome and hasattr(affittante_nome, 'username') else affitto.affittante,
            'affittuario_nome': affittuario_nome.username if affittuario_nome and hasattr(affittuario_nome, 'username') else affitto.affittuario,
        })
    # Prenotazioni: tutte le prenotazioni dell'utente
    prenotazioni = AutoPrenotazione.objects.filter(prenotante_id=user.id).select_related('auto')
    prenotazioni_info = []
    for pren in prenotazioni:
        prenotante_nome = User.objects.filter(id=pren.prenotante_id).first()
        prenotazioni_info.append({
            'prenotazione': pren,
            'prenotante_nome': prenotante_nome.username if prenotante_nome else pren.prenotante_id,
        })
    # Contrattazioni: tutte le contrattazioni dell'utente
    contrattazioni_iniziate = AutoContrattazione.objects.filter(acquirente_id=user.id, acquirente_tipologia='Utente').select_related('auto')
    contrattazioni_ricevute = AutoContrattazione.objects.filter(venditore_id=user.id, venditore_tipologia='Utente').select_related('auto')

    # Chat per contrattazioni iniziate
    chat_ids_iniziate = {}
    for contr in contrattazioni_iniziate:
        auto = contr.auto
        venditore = auto.user_auto
        acquirente = user
        chat = ChatRoom.objects.filter(
            Q(user_1=acquirente, user_2=venditore) | Q(user_1=venditore, user_2=acquirente),
            auto_chat=auto
        ).first()
        chat_ids_iniziate[contr.id] = chat.id if chat else None

    # Chat per contrattazioni ricevute
    chat_ids_ricevute = {}
    for contr in contrattazioni_ricevute:
        auto = contr.auto
        venditore = user
        try:
            acquirente = User.objects.get(id=contr.acquirente_id)
        except User.DoesNotExist:
            acquirente = None
        if acquirente:
            chat = ChatRoom.objects.filter(
                Q(user_1=acquirente, user_2=venditore) | Q(user_1=venditore, user_2=acquirente),
                auto_chat=auto
            ).first()
            chat_ids_ricevute[contr.id] = chat.id if chat else None
        else:
            chat_ids_ricevute[contr.id] = None

    # Chat per affitti
    chat_ids_affitti = {}
    for info in affitti_info:
        affitto = info['affitto']
        auto = affitto.auto
        # Trova l'altro utente coinvolto
        if affitto.affittante == user.id:
            try:
                other_user = User.objects.get(id=affitto.affittuario)
            except User.DoesNotExist:
                other_user = None
        else:
            try:
                other_user = User.objects.get(id=affitto.affittante)
            except User.DoesNotExist:
                other_user = None
        if other_user:
            chat = ChatRoom.objects.filter(
                Q(user_1=user, user_2=other_user) | Q(user_1=other_user, user_2=user),
                auto_chat=auto
            ).first()
            chat_ids_affitti[affitto.id] = chat.id if chat else None
        else:
            chat_ids_affitti[affitto.id] = None

    # Chat per prenotazioni
    chat_ids_prenotazioni = {}
    for info in prenotazioni_info:
        pren = info['prenotazione']
        auto = pren.auto
        try:
            proprietario = auto.user_auto
        except Exception:
            proprietario = None
        if proprietario and proprietario != user:
            chat = ChatRoom.objects.filter(
                Q(user_1=user, user_2=proprietario) | Q(user_1=proprietario, user_2=user),
                auto_chat=auto
            ).first()
            chat_ids_prenotazioni[pren.id] = chat.id if chat else None
        else:
            chat_ids_prenotazioni[pren.id] = None

    return render(request, 'Utente/gestione_auto.html', {
        'auto_list': auto_list,
        'affitti_info': affitti_info,
        'prenotazioni_info': prenotazioni_info,
        'contrattazioni_iniziate': contrattazioni_iniziate,
        'contrattazioni_ricevute': contrattazioni_ricevute,
        'user_extend': user,
        'chat_ids_iniziate': chat_ids_iniziate,
        'chat_ids_ricevute': chat_ids_ricevute,
        'chat_ids_affitti': chat_ids_affitti,
        'chat_ids_prenotazioni': chat_ids_prenotazioni,
    })

@login_required
def gestione_auto_view(request):
    #Sezione controllo utente
    user = request.user
    try:
        if not request.user.groups.filter(name="utente").exists():
            messages.error(request, "Accesso riservato agli utenti.")
            return redirect('home')
    except UserExtendModel.DoesNotExist:
        UserExtendModel.objects.create(user=request.user)

    user_extend = UserExtendModel.objects.get(user=user)
    auto_mie = Auto.objects.filter(user_auto=user)

    #Sezione affitto
    #Sezione auto affittate da me
    auto_affitto_mie = AutoAffitto.objects.filter(affittante=user.id)
    chat_affitto_mie = ChatRoom.objects.filter(auto_chat__in=auto_affitto_mie.values_list('auto', flat=True))
    utenti_che_hanno_affittato_da_me = {
        user_obj.id: user_obj.username for user_obj in User.objects.filter(id__in=auto_affitto_mie.values_list('affittuario', flat=True).distinct())
    }
    # Dizionario: affitto.id -> chat.id (mie)
    chat_affitto_mie_dict = {}
    for affitto in auto_affitto_mie:
        chat = ChatRoom.objects.filter(auto_chat=affitto.auto, user_1__in=[affitto.affittante, affitto.affittuario], user_2__in=[affitto.affittante, affitto.affittuario]).first()
        chat_affitto_mie_dict[affitto.id] = chat.id if chat else None

    #Sezione auto mie in affitto
    auto_affitto_non_mie = AutoAffitto.objects.filter(affittuario=user.id)
    chat_affitto_non_mie = ChatRoom.objects.filter(auto_chat__in=auto_affitto_non_mie.values_list('auto', flat=True))
    utenti_che_hanno_affittato_a_me = {
        user_obj.id: user_obj.username for user_obj in User.objects.filter(id__in=auto_affitto_non_mie.values_list('affittante', flat=True).distinct())
    }
    # Dizionario: affitto.id -> chat.id (non mie)
    chat_affitto_non_mie_dict = {}
    for affitto in auto_affitto_non_mie:
        chat = ChatRoom.objects.filter(auto_chat=affitto.auto, user_1__in=[affitto.affittante, affitto.affittuario], user_2__in=[affitto.affittante, affitto.affittuario]).first()
        chat_affitto_non_mie_dict[affitto.id] = chat.id if chat else None

    almeno_uno_affittata = False
    for auto_affitto in auto_affitto_mie:
        if auto_affitto.affittata:
            almeno_uno_affittata = True
            break
    if not almeno_uno_affittata:
        for auto_affitto in auto_affitto_non_mie:
            if auto_affitto.affittata:
                almeno_uno_affittata = True
                break
    #Sezione prenotazioni
    #Sezione prenotazioni effettuate
    auto_prenotate = AutoPrenotazione.objects.filter(prenotante_id=user.id)
    chat_prenotate = ChatRoom.objects.filter(auto_chat__in=auto_prenotate.values_list('auto', flat=True))
    utenti_da_cui_ho_prenotato = {
        user_obj.id: user_obj.username for user_obj in User.objects.filter(id__in=auto_prenotate.values_list('auto__user_auto', flat=True).distinct())
    }
    # Dizionario: prenotazione.id -> chat.id
    chat_prenotate_dict = {}
    for pren in auto_prenotate:
        chat = ChatRoom.objects.filter(auto_chat=pren.auto, user_1__in=[pren.prenotante_id, pren.auto.user_auto.id], user_2__in=[pren.prenotante_id, pren.auto.user_auto.id]).first()
        chat_prenotate_dict[pren.id] = chat.id if chat else None

    #Sezione contrattazioni
    #Sezione contr avviate
    contr_iniziate = AutoContrattazione.objects.filter(acquirente_id=user.id)
    chat_contr_iniziate = ChatRoom.objects.filter(auto_chat__in=contr_iniziate.values_list('auto', flat=True))
    utenti_a_cui_ho_iniziato_contr = {
        user_obj.id: user_obj.username for user_obj in User.objects.filter(id__in=contr_iniziate.values_list('venditore_id', flat=True).distinct())
    }
    # Dizionario: contrattazione.id -> chat.id (iniziate)
    chat_contr_iniziate_dict = {}
    for contr in contr_iniziate:
        chat = ChatRoom.objects.filter(auto_chat=contr.auto, user_1__in=[contr.acquirente_id, contr.venditore_id], user_2__in=[contr.acquirente_id, contr.venditore_id]).first()
        chat_contr_iniziate_dict[contr.id] = chat.id if chat else None

    #Sezione contr ricevute
    contr_ricevute = AutoContrattazione.objects.filter(venditore_id=user.id)
    chat_contr_ricevute = ChatRoom.objects.filter(auto_chat__in=contr_ricevute.values_list('auto', flat=True))
    utenti_da_cui_ho_ricevuto_contr = {
        user_obj.id: user_obj.username for user_obj in User.objects.filter(id__in=contr_ricevute.values_list('acquirente_id', flat=True).distinct())
    }
    # Dizionario: contrattazione.id -> chat.id (ricevute)
    chat_contr_ricevute_dict = {}
    for contr in contr_ricevute:
        chat = ChatRoom.objects.filter(auto_chat=contr.auto, user_1__in=[contr.acquirente_id, contr.venditore_id], user_2__in=[contr.acquirente_id, contr.venditore_id]).first()
        chat_contr_ricevute_dict[contr.id] = chat.id if chat else None

     # Render della pagina con i dati raccolti

    return render(request, 'Utente/gestione_auto.html', {
        'auto_affitto_mie': auto_affitto_mie,
        'chat_affitto_mie': chat_affitto_mie,
        'chat_affitto_mie_dict': chat_affitto_mie_dict,
        'utenti_che_hanno_affittato_da_me': utenti_che_hanno_affittato_da_me,

        'auto_affitto_non_mie': auto_affitto_non_mie,
        'chat_affitto_non_mie': chat_affitto_non_mie,
        'chat_affitto_non_mie_dict': chat_affitto_non_mie_dict,
        'utenti_che_hanno_affittato_a_me': utenti_che_hanno_affittato_a_me,

        'auto_prenotate': auto_prenotate,
        'chat_prenotate': chat_prenotate,
        'chat_prenotate_dict': chat_prenotate_dict,
        'utenti_da_cui_ho_prenotato': utenti_da_cui_ho_prenotato,

        'contr_iniziate': contr_iniziate,
        'chat_contr_iniziate': chat_contr_iniziate,
        'chat_contr_iniziate_dict': chat_contr_iniziate_dict,
        'utenti_a_cui_ho_iniziato_contr': utenti_a_cui_ho_iniziato_contr,

        'contr_ricevute': contr_ricevute,
        'chat_contr_ricevute': chat_contr_ricevute,
        'chat_contr_ricevute_dict': chat_contr_ricevute_dict,
        'utenti_da_cui_ho_ricevuto_contr': utenti_da_cui_ho_ricevuto_contr,

        'almeno_uno_affittata': almeno_uno_affittata,

        'self_user': user,
        'self_user_extend': user_extend,
    })
