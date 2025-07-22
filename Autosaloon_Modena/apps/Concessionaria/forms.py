from django import forms
from django.contrib.auth import authenticate

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
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ''}), required=True)

    class Meta:
        model = Concessionaria
        fields = ['email', 'nome', 'indirizzo', 'telefono', 'partita_iva', 'codice_fiscale', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'indirizzo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'partita_iva': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'codice_fiscale': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
        }

class ConcessionariaUpdateForm(forms.ModelForm):
    class Meta:
        model = Concessionaria
        fields = ['email', 'nome', 'indirizzo', 'telefono', 'partita_iva', 'codice_fiscale']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'indirizzo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'partita_iva': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'codice_fiscale': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
        }
