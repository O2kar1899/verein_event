from django import forms

from .models import EventModel, EventRegistration


class EventForm(forms.ModelForm):
    class Meta:
        model = EventModel
        fields = ['title','description','location','target_group', 'start_date',
                  'end_date', 'event_url','is_public', 'organization', 
                  'registration_required', 'max_participants']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Felder optional machen
        self.fields['event_url'].required = False
        self.fields['organization'].required = False
        self.fields['description'].required = False
        self.fields['location'].required = False
        self.fields['target_group'].required = False
        self.fields['end_date'].required = False
        self.fields['max_participants'].required = False
                
        # Platzhalter hinzufügen
        self.fields['event_url'].widget.attrs['placeholder'] = 'https://... (optional)'
        self.fields['description'].widget.attrs['placeholder'] = 'Beschreibung des Events (optional)'
        self.fields['location'].widget.attrs['placeholder'] = 'Veranstaltungsort (optional)'
        self.fields['target_group'].widget.attrs['placeholder'] = 'Zielgruppe (optional)'

class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['first_name', 'last_name', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'
            })

class EmailLookupForm(forms.Form):
    email = forms.EmailField(
        label='Ihre E-Mail-Adresse',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Ihre E-Mail-Adresse'
        })
    )