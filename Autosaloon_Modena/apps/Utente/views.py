from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LogoutView
from .models import UserExtendModel
from .form import UserCreateForm, UserExtendForm, UserUpdateForm, UserDeleteForm, CommentoForm, RispostaForm, SegnalazioneForm

# Creazione utente base + profilo esteso
class UserCreateView(CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'Utente/create_user.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        UserExtendModel.objects.create(user=user)
        # Autenticazione e login automatico dopo la registrazione
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

# Modifica utente base
class UserUpdateView(UpdateView):
    model = UserExtendModel
    form_class = UserUpdateForm
    template_name = 'Utente/update_user.html'
    success_url = reverse_lazy('home')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

# Eliminazione utente
class UserDeleteView(DeleteView):
    model = UserExtendModel
    template_name = 'Utente/delete_user.html'
    success_url = reverse_lazy('home')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

# Creazione commento
class CommentoCreateView(CreateView):
    form_class = CommentoForm
    template_name = 'Utente/create_commento.html'
    success_url = reverse_lazy('home')

# Creazione risposta
class RispostaCreateView(CreateView):
    form_class = RispostaForm
    template_name = 'Utente/create_risposta.html'
    success_url = reverse_lazy('home')

# Creazione segnalazione
class SegnalazioneCreateView(CreateView):
    form_class = SegnalazioneForm
    template_name = 'Utente/create_segnalazione.html'
    success_url = reverse_lazy('home')

# View per il logout utente
class UserLogoutView(LogoutView):
    next_page = 'home'
