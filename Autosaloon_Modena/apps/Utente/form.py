from django import forms
from django.contrib.auth.models import User
from .models import UserExtendModel

class UserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
        widgets = {
            'password': forms.PasswordInput(),
        }

class UserExtendForm(forms.ModelForm):
    class Meta:
        model = UserExtendModel
        fields = ['data_nascita', 'indirizzo', 'telefono', 'immagine_profilo']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

class UserDeleteForm(forms.Form):
    confirm = forms.BooleanField(label='Conferma eliminazione utente')

# Placeholder per Commento, Risposta, Segnalazione
class CommentoForm(forms.Form):
    testo = forms.CharField(widget=forms.Textarea)

class RispostaForm(forms.Form):
    testo = forms.CharField(widget=forms.Textarea)

class SegnalazioneForm(forms.Form):
    motivo = forms.CharField(widget=forms.Textarea)

