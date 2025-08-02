from django import forms
from django.contrib.auth.models import User
from .models import UserExtendModel, Segnalazione
from apps.Auto.models import Commento, Risposta

class UserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
        }

class UserExtendForm(forms.ModelForm):
    class Meta:
        model = UserExtendModel
        fields = ['data_nascita', 'indirizzo', 'telefono', 'immagine_profilo']
        widgets = {
            'data_nascita': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': ''}),
            'indirizzo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'immagine_profilo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
        }

class UserDeleteForm(forms.Form):
    confirm = forms.BooleanField(label='Conferma eliminazione utente', widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

# Placeholder per Commento, Risposta, Segnalazione
class CommentoForm(forms.ModelForm):
    class Meta:
        model = Commento
        fields = ['testo']
        widgets = {
            'testo': forms.Textarea(attrs={'class': 'form-control', 'placeholder': ''}),
        }

class RispostaForm(forms.ModelForm):
    class Meta:
        model = Risposta
        fields = ['testo']
        widgets = {
            'testo': forms.Textarea(attrs={'class': 'form-control', 'placeholder': ''}),
        }

class SegnalazioneForm(forms.ModelForm):
    class Meta:
        model = Segnalazione
        fields = ['motivo']
        widgets = {
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'placeholder': ''}),
        }

class UserFullUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ''}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}))
    data_nascita = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': ''}))
    indirizzo = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}))
    telefono = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}))
    immagine_profilo = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserExtendModel
        fields = ['email', 'first_name', 'last_name', 'data_nascita', 'indirizzo', 'telefono', 'immagine_profilo']

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        if instance:
            initial.update({
                'email': instance.user.email,
                'first_name': instance.user.first_name,
                'last_name': instance.user.last_name,
                'data_nascita': instance.data_nascita,
                'indirizzo': instance.indirizzo,
                'telefono': instance.telefono,
                'immagine_profilo': instance.immagine_profilo,
            })
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        user_extend = super().save(commit=False)
        user = user_extend.user
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            user_extend.save()
            if self.cleaned_data.get('immagine_profilo'):
                user_extend.immagine_profilo = self.cleaned_data['immagine_profilo']
                user_extend.save()
        return user_extend
