from datetime import timezone, datetime, timedelta

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView

from .auto_utils import gestione_vendita_affitto
from .form import AddAutoForm, ModifyAutoForm, AffittoAutoForm, PrenotazioneAutoForm, VenditaAutoForm, ContrattoAutoForm
from .models import Auto, AutoAffitto, AutoVendita, AutoPrenotazione, AutoContrattazione
from ..decorator import user_or_concessionaria_required
from ..utils import user_or_concessionaria, get_success_url_by_possessore, is_possessore_auto



@method_decorator(user_or_concessionaria_required, name='dispatch')
class AutoAddView(CreateView):
    model = Auto
    template_name = 'Auto/add_auto.html'
    form_class = AddAutoForm

    def form_valid(self, form):
        auto = form.save(commit=False)
        auto.tipologia_possessore, auto.id_possessore = user_or_concessionaria(self.request.user)
        auto.save()
        prezzo_vendita = form.cleaned_data.get('prezzo_vendita')
        prezzo_affitto = form.cleaned_data.get('prezzo_affitto')
        if prezzo_vendita:
            AutoVendita.objects.create(auto=auto, prezzo_vendita=prezzo_vendita, venditore_id=auto.id_possessore, venditore_tipologia=auto.tipologia_possessore)
        if prezzo_affitto:
            AutoAffitto.objects.create(auto=auto, prezzo_affitto=prezzo_affitto, affittante_id=auto.id_possessore, affittante_tipologia=auto.tipologia_possessore)
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)



@method_decorator(user_or_concessionaria_required, name='dispatch')
class AutoDeleteView(DeleteView):
    model = Auto
    template_name = 'Auto/delete_auto.html'

    def delete(self, request, *args, **kwargs):
        auto = self.get_object()
        tipologia, id_possessore = user_or_concessionaria(request.user)
        if is_possessore_auto(tipologia, id_possessore, auto):
            # Elimina le istanze collegate in AutoVendita e AutoAffitto
            AutoVendita.objects.filter(auto=auto).delete()
            AutoAffitto.objects.filter(auto=auto).delete()
            return super().delete(request, *args, **kwargs)
        else:
            return HttpResponse("Non sei il possessore di questa auto.", status=403)

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)



@method_decorator(user_or_concessionaria_required, name='dispatch')
class AutoModifyView(UpdateView):
    model = Auto
    template_name = 'Auto/modify_auto.html'
    form_class = ModifyAutoForm

    def form_valid(self, form):
        auto = form.save(commit=False)
        auto.tipologia_possessore, auto.id_possessore = user_or_concessionaria(self.request.user)
        if is_possessore_auto(auto.tipologia_possessore, auto.id_possessore, auto.id):
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
        else:
            return HttpResponse("Non sei il possessore di questa auto.", status=403)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form, 'auto': self.get_object()})

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)



@method_decorator(user_or_concessionaria_required, name='dispatch')
class AutoAffittoView(UpdateView):
    model = AutoAffitto
    form_class = AffittoAutoForm
    template_name = 'Auto/affitto_auto.html'

    def form_valid(self, form):
        affitto = form.save(commit=False)
        affitto.auto = self.get_object()
        affitto.affittuario_id, affitto.affittuario_tipologia = user_or_concessionaria(self.request.user)
        affitto.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form, 'auto': self.get_object()})

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)



@method_decorator(user_or_concessionaria_required, name='dispatch')
class AutoAcquistoView(UpdateView):
    model = AutoVendita
    form_class = VenditaAutoForm  # Assuming the same form is used for both
    template_name = 'Auto/acquisto_auto.html'

    def form_valid(self, form):
        vendita = form.save(commit=False)
        vendita.auto = self.get_object()
        vendita.venditore = self.request.user
        vendita.data_pubblicazione = datetime.now()
        auto = vendita.auto
        auto.tipologia_possessore, auto.id_possessore = user_or_concessionaria(self.request.user)
        auto_affitto = AutoAffitto.objects.filter(auto=auto).first()
        if auto_affitto:
            auto_affitto.affittuario_tipologia, auto_affitto.affittuario_id = user_or_concessionaria(self.request.user)
            auto_affitto.affittante_id, auto_affitto.affittante_tipologia = None, None
        auto_affitto.save()
        auto.save()
        vendita.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return render(self.request, self.template_name, {'form': form})

    def get_success_url(self):
        return get_success_url_by_possessore(self.request)



@method_decorator(user_or_concessionaria_required, name='dispatch')
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


@method_decorator(user_or_concessionaria_required, name='dispatch')
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


@method_decorator(user_or_concessionaria_required, name='dispatch')
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



