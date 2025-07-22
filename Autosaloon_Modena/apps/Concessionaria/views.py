from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Concessionaria
from .forms import ConcessionariaForm, ConcessionariaUpdateForm, ConcessionariaLoginForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django import forms
from django.contrib.auth import authenticate

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

class ConcessionariaRegistrationView(CreateView):
    model = Concessionaria
    form_class = ConcessionariaForm
    template_name = 'Concessionaria/registration_form.html'
    success_url = '/accounts/register/complete/'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.set_password(form.cleaned_data['password'])
        obj.save()
        messages.success(self.request, 'Registrazione avvenuta con successo! Ora puoi accedere.')
        return super().form_valid(form)

class ConcessionariaLoginView(LoginView):
    template_name = 'Concessionaria/login.html'
    authentication_form = ConcessionariaLoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Rimuovo 'request' se presente
        kwargs.pop('request', None)
        return kwargs

    def get_success_url(self):
        return self.success_url
