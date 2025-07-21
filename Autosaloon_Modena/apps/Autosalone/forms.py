from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['receiver_content_type', 'receiver_object_id', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Scrivi il tuo messaggio...'}),
        }

