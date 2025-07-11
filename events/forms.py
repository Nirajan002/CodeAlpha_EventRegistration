from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'capacity']
        widgets = {
            'date': forms.DateTimeInput(attrs={
                'placeholder': 'YYYY-MM-DD H:i',
                'type': 'text' 
            }),
        }
