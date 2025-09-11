# eventapp/forms.py - Korrigierte Version
from authapp.models import Organization, UserProfile
from django import forms
from django.core.exceptions import ValidationError

from .models import EventModel, EventRegistration


class EventForm(forms.ModelForm):
    class Meta:
        model = EventModel
        fields = ['title', 'description', 'location', 'target_group', 'start_date',
                  'end_date', 'event_url', 'is_public', 'organization', 
                  'registration_required', 'max_participants']
        widgets = {
            'start_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'end_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'description': forms.Textarea(
                attrs={'rows': 4, 'class': 'form-control'}
            ),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'target_group': forms.TextInput(attrs={'class': 'form-control'}),
            'event_url': forms.URLInput(attrs={'class': 'form-control'}),
            'organization': forms.Select(attrs={'class': 'form-control'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
        labels = {
            'title': 'Veranstaltungstitel',
            'description': 'Beschreibung',
            'location': 'Veranstaltungsort',
            'target_group': 'Zielgruppe',
            'start_date': 'Startdatum',
            'end_date': 'Enddatum',
            'event_url': 'Event-URL',
            'is_public': 'Öffentlich sichtbar',
            'organization': 'Organisation',
            'registration_required': 'Anmeldung erforderlich',
            'max_participants': 'Maximale Teilnehmerzahl',
        }

    def __init__(self, *args, **kwargs):
        # User aus kwargs extrahieren
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # DEBUG: Temporär hinzufügen
        print(f"DEBUG FORM: User = {self.user}")
        
        # Felder optional machen
        self.fields['event_url'].required = False
        self.fields['organization'].required = False
        self.fields['description'].required = False
        self.fields['location'].required = False
        self.fields['target_group'].required = False
        self.fields['end_date'].required = False
        self.fields['max_participants'].required = False
        
        # Wenn User vorhanden ist, Organization-Queryset filtern
        if self.user and self.user.is_authenticated:
            try:
                user_profile, created = UserProfile.objects.get_or_create(user=self.user)
                # DEBUG
                print(f"DEBUG FORM: UserProfile gefunden/erstellt, Organizations: {user_profile.organizations.all()}")
                
                # Nur Organisationen anzeigen, für die der User freigeschaltet ist
                if user_profile.organizations.exists():
                    self.fields['organization'].queryset = user_profile.organizations.all()
                    self.fields['organization'].empty_label = "-- Wählen Sie eine Organisation --"
                else:
                    # Wenn keine Organisationen freigeschaltet sind, feld deaktivieren
                    self.fields['organization'].queryset = Organization.objects.none()
                    self.fields['organization'].empty_label = "-- Keine Organisationen verfügbar --"
                    self.fields['organization'].help_text = "Sie sind für keine Organisation freigeschaltet."
                    
            except Exception as e:
                print(f"DEBUG FORM: Fehler beim Abrufen des UserProfiles: {e}")
                self.fields['organization'].queryset = Organization.objects.none()
                self.fields['organization'].empty_label = "-- Keine Organisationen verfügbar --"
        else:
            # Wenn kein User, alle Organisationen deaktivieren
            self.fields['organization'].queryset = Organization.objects.none()
            self.fields['organization'].empty_label = "-- Bitte einloggen --"
            
        # Hilfetexte hinzufügen
        self.fields['registration_required'].help_text = "Aktivieren Sie dies, wenn eine Anmeldung erforderlich ist"
        self.fields['max_participants'].help_text = "Leer lassen für unbegrenzte Teilnehmerzahl"
        self.fields['is_public'].help_text = "Öffentliche Events sind für alle sichtbar"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        registration_required = cleaned_data.get('registration_required')
        max_participants = cleaned_data.get('max_participants')
        
        # Validierung: Enddatum muss nach Startdatum sein
        if start_date and end_date:
            if end_date < start_date:
                raise ValidationError(
                    "Das Enddatum muss nach dem Startdatum liegen."
                )
        
        # Validierung: Bei Anmeldung erforderlich sollte max_participants gesetzt sein
        if registration_required and not max_participants:
            self.add_error('max_participants', 
                          'Bei erforderlicher Anmeldung sollte eine maximale Teilnehmerzahl angegeben werden.')
        
        # Validierung: Organisation prüfen
        organization = cleaned_data.get('organization')
        if organization and self.user:
            try:
                user_profile = UserProfile.objects.get(user=self.user)
                if organization not in user_profile.organizations.all():
                    raise ValidationError(
                        f"Sie sind nicht für die Organisation '{organization.name}' freigeschaltet."
                    )
            except UserProfile.DoesNotExist:
                raise ValidationError("Benutzerprofil nicht gefunden.")
        
        return cleaned_data


class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = EventRegistration
        fields = ['first_name', 'last_name', 'email', 'phone', 'notes']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'email': 'E-Mail-Adresse',
            'phone': 'Telefonnummer',
            'notes': 'Bemerkungen',
        }
        help_texts = {
            'email': 'Wir verwenden Ihre E-Mail-Adresse für die Anmeldebestätigung.',
            'phone': 'Optional: Für Rückfragen',
            'notes': 'Optional: Besondere Anforderungen oder Bemerkungen',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Telefon und Notizen optional machen
        self.fields['phone'].required = False
        self.fields['notes'].required = False

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # E-Mail in Kleinbuchstaben normalisieren
            email = email.lower().strip()
        return email


class EmailLookupForm(forms.Form):
    email = forms.EmailField(
        label='E-Mail-Adresse',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ihre.email@beispiel.de',
            'required': True
        }),
        help_text='Geben Sie Ihre E-Mail-Adresse ein, um Ihre Registrierungen anzuzeigen.'
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # E-Mail in Kleinbuchstaben normalisieren
            email = email.lower().strip()
        return email


class EventFilterForm(forms.Form):
    """Optional: Formular zum Filtern von Events in der Liste"""
    organization = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        required=False,
        empty_label="-- Alle Organisationen --",
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        label='Organisation'
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Suche nach Titel oder Beschreibung...'
        }),
        label='Suche'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Von Datum'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500'
        }),
        label='Bis Datum'
    )
    
    only_public = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'}),
        label='Nur öffentliche Events'
    )
    
    registration_open = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'}),
        label='Nur Events mit offener Anmeldung'
    )