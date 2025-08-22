from django import forms
from .models import Auto, AutoAffitto, AutoVendita, AutoContrattazione, AutoListaAffitto, AutoPrenotazione


class AddAutoForm(forms.ModelForm):
    prezzo_vendita = forms.DecimalField(required=False, decimal_places=2, max_digits=10, label='Prezzo di Vendita')
    prezzo_affitto = forms.DecimalField(required=False, decimal_places=2, max_digits=10, label='Prezzo di Affitto')
    class Meta:
        model = Auto
        fields = [
            'marca', 'modello', 'cilindrata', 'carburante', 'cambio', 'trazione', 'anno',
            'disponibilita', 'chilometraggio', 'descrizione', 'immagine'
        ]
        widgets = {
            'descrizione': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'immagine': forms.ClearableFileInput(attrs={'multiple': False})
        }

class ModifyAutoForm(forms.ModelForm):
    prezzo_vendita = forms.DecimalField(required=False, decimal_places=2, max_digits=10, label='Prezzo di Vendita')
    prezzo_affitto = forms.DecimalField(required=False, decimal_places=2, max_digits=10, label='Prezzo di Affitto')
    class Meta:
        model = Auto
        fields = [
            'marca', 'modello', 'cilindrata', 'carburante', 'cambio', 'trazione', 'anno',
            'disponibilita', 'chilometraggio', 'descrizione', 'immagine'
        ]
        widgets = {
            'descrizione': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'immagine': forms.ClearableFileInput(attrs={'multiple': False})
        }

class AffittoAutoForm(forms.ModelForm):
    class Meta:
        model = AutoAffitto
        fields = [
            'data_inizio', 'data_fine'
        ]
        widgets = {
            'data_inizio': forms.DateInput(attrs={'type': 'date'}),
            'data_fine': forms.DateInput(attrs={'type': 'date'}),
        }

class AffittoAutoListaForm(forms.ModelForm):
    class Meta:
        model = AutoListaAffitto
        fields = [
            'data_inizio', 'data_fine'
        ]
        widgets = {
            'data_inizio': forms.DateInput(attrs={'type': 'date'}),
            'data_fine': forms.DateInput(attrs={'type': 'date'}),
        }

class VenditaAutoForm(forms.ModelForm):
    class Meta:
        model = AutoVendita
        fields = []

class ContrattoAutoForm(forms.ModelForm):
    class Meta:
        model = AutoContrattazione
        fields = [
            'prezzo_attuale'
        ]
        widgets = {
            'prezzo_attuale': forms.NumberInput(attrs={'step': '0.01'})
        }

class PrenotazioneAutoForm(forms.ModelForm):
    class Meta:
        model = AutoPrenotazione
        fields = []

