from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Concessionaria, ConcessionariaExtendModel
from .form import ConcessionariaForm, ConcessionariaUpdateForm, ConcessionariaLoginForm, ConcessionariaCreateForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate

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
        Concessionaria.objects.create(user=user)
        Concessionaria.partita_iva = form.cleaned_data['partita_iva']
        Concessionaria.codice_fiscale = form.cleaned_data['codice_fiscale']
        # Autenticazione e login automatico dopo la registrazione
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'], email=form.cleaned_data['email'])
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

class ConcessionariaUpdateView(UpdateView):
    model = Concessionaria
    form_class = ConcessionariaUpdateForm
    template_name = 'Concessionaria/concessionaria_form.html'
    success_url = reverse_lazy('concessionaria-list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

class ConcessionariaDeleteView(DeleteView):
    model = Concessionaria
    template_name = 'Concessionaria/concessionaria_confirm_delete.html'
    success_url = reverse_lazy('concessionaria-list')
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
