from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Concessionaria
from .forms import ConcessionariaForm, ConcessionariaUpdateForm

class ConcessionariaCreateView(CreateView):
    model = Concessionaria
    form_class = ConcessionariaForm
    template_name = 'Concessionaria/concessionaria_form.html'
    success_url = reverse_lazy('concessionaria-list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.set_password(form.cleaned_data['password'])
        obj.save()
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
