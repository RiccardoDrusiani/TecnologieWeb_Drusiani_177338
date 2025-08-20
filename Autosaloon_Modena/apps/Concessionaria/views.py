from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Concessionaria, HistoryVendute
from .form import ConcessionariaUpdateForm, ConcessionariaCreateForm, ConcessionariaFullUpdateForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from ..Auto.models import Auto


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
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user = self.object.user
        Auto.objects.filter(user_auto=user).delete()
        user.delete()
        logout(request)
        request.session.flush()
        return redirect(self.success_url)

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return self.success_url

class ConcessionariaLoginView(LoginView):
    # ...existing code...
    def form_invalid(self, form):
        messages.error(self.request, "Email o password non validi.")
        return redirect('concessionaria-login')

@login_required
def impostazioni_concessionaria(request):
    try:
        concessionaria_profile = request.user.concessionaria_profile
    except Concessionaria.DoesNotExist:
        concessionaria_profile = Concessionaria.objects.create(user=request.user)
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
        # Placeholder: in futuro sostituire con query reali
        contrattazioni_avviate = []  # Contrattazioni avviate dalla concessionaria
        contrattazioni_ricevute = [] # Contrattazioni ricevute da altri
        # filterset = AutoFilterSet(request.GET, queryset=Auto.objects.all())
        return render(request, 'Concessionaria/contrattazioni.html', {
            'contrattazioni_avviate': contrattazioni_avviate,
            'contrattazioni_ricevute': contrattazioni_ricevute,
            # 'filter': filterset,
        })

class AutoVenduteView(LoginRequiredMixin, View):
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

class AutoAffittateView(LoginRequiredMixin, View):
    def get(self, request):
        # Filtro solo auto affittate (disponibilita = 'affittata')
        concessionaria = getattr(self.request.user, 'concessionaria_profile', None)
        if concessionaria:
            auto_affittate = HistoryVendute.objects.filter(concessionaria=concessionaria.user)
        else:
            auto_affittate = HistoryVendute.objects.none()
        # filterset = AutoFilterSet(request.GET, queryset=Auto.objects.all())
        return render(request, 'Concessionaria/auto_affittate.html', {
            'auto_affittate': auto_affittate,
            # 'filter': filterset,
        })

# La casella di posta usa la MessageListView già esistente in Autosalone.views
