from django import forms
from .models import Concessionaria

class ConcessionariaForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Concessionaria
        fields = ['email', 'nome', 'indirizzo', 'telefono', 'partita_iva', 'codice_fiscale', 'password']

class ConcessionariaUpdateForm(forms.ModelForm):
    class Meta:
        model = Concessionaria
        fields = ['email', 'nome', 'indirizzo', 'telefono', 'partita_iva', 'codice_fiscale']

