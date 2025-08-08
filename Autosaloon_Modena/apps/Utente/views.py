from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User, Group
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib import messages
from .models import UserExtendModel, Segnalazione, UserModelBan
from .form import UserCreateForm, UserExtendForm, UserUpdateForm, UserDeleteForm, CommentoForm, RispostaForm, SegnalazioneForm, UserFullUpdateForm
from ..Auto.models import Commento, Risposta, Auto, AutoVendita, AutoAffitto
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.utils import timezone
from django.utils.decorators import method_decorator

from ..decorator import user_is_banned


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
class UserUpdateView(UpdateView):
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
class UserDeleteView(DeleteView):
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
class CommentoCreateView(CreateView):
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

    def form_invalid(self, form):
        messages.error(self.request, "Email o password non validi.")
        return redirect('login')

@login_required
def impostazioni_utente(request):
    try:
        user_profile = request.user.user_extend_profile
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
