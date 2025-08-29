from django import forms

from .models import EventModel


class EventForm(forms.ModelForm):
    class Meta:
        model = EventModel
        fields = ['title', 'event_url', 'organization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Felder optional machen
        self.fields['event_url'].required = False
        self.fields['organization'].required = False
        # Platzhalter hinzufügen
        self.fields['event_url'].widget.attrs['placeholder'] = 'https://... (optional)'