from django import forms

from .models import EventModel


class EventForm(forms.ModelForm):
    class Meta:
        model = EventModel
        fields = ['title','description','location','target_group','start_date','end_date', 'event_url','is_public', 'organization']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Felder optional machen
        self.fields['event_url'].required = False
        self.fields['organization'].required = False
        self.fields['description'].required = False
        self.fields['location'].required = False
        self.fields['target_group'].required = False
        self.fields['end_date'].required = False
        
        # Platzhalter hinzufügen
        self.fields['event_url'].widget.attrs['placeholder'] = 'https://... (optional)'
        self.fields['description'].widget.attrs['placeholder'] = 'Beschreibung des Events (optional)'
        self.fields['location'].widget.attrs['placeholder'] = 'Veranstaltungsort (optional)'
        self.fields['target_group'].widget.attrs['placeholder'] = 'Zielgruppe (optional)'

    