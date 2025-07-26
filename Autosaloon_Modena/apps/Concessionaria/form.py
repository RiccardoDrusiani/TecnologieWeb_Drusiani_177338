from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Concessionaria

class ConcessionariaLoginForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ''}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ''}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError('Email o password non validi')
            cleaned_data['user'] = user
        return cleaned_data

    def get_user(self):
        return self.cleaned_data.get('user', None)

class ConcessionariaForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ''}), required=True)
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ''}), required=True)

    class Meta:
        model = Concessionaria
        fields = ['username', 'email', 'password', 'partita_iva', 'codice_fiscale']
        widgets = {
            'partita_iva': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'codice_fiscale': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
        }

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        concessionaria = super().save(commit=False)
        concessionaria.user = user
        if commit:
            concessionaria.save()
        return concessionaria

class ConcessionariaUpdateForm(forms.ModelForm):
    class Meta:
        model = Concessionaria
        fields = ['partita_iva', 'codice_fiscale']
        widgets = {
            'partita_iva': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'codice_fiscale': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
        }

class ConcessionariaCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    conferma_password = forms.CharField(widget=forms.PasswordInput, label="Conferma Password")
    partita_iva = forms.CharField(max_length=11, label="Partita IVA")
    codice_fiscale = forms.CharField(max_length=16, label="Codice Fiscale")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        conferma_password = cleaned_data.get('conferma_password')
        if password != conferma_password:
            raise ValidationError("Le password non corrispondono.")
        return cleaned_data
