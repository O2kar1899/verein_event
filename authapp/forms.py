from django import forms
from django.contrib.auth.forms import UserCreationForm  # Dieser Import fehlte
from django.contrib.auth.models import User

from .models import Organization, OrganizationAccessRequest, UserProfile


class UserProfileForm(UserCreationForm):

    phone = forms.CharField(
        max_length=15, 
        required=False,
        label="Telefonnummer",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all'
        })
    )
    vereine = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Vereine"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'username': 'Benutzername',
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'email': 'E-Mail',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Styling für Passwortfelder
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all'
        })



class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'organization_url', 'street', 'post_code', 'city']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Name der Organisation',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'
            }),
            'organization_url': forms.URLInput(attrs={
                'placeholder': 'https://...',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'
            }),
            'street': forms.TextInput(attrs={
                'placeholder': 'Straße und Hausnummer (optional)',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'
            }),
            'post_code': forms.TextInput(attrs={
                'placeholder': '12345',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'Stadt (optional)',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['street'].required = False
        self.fields['city'].required = False


class OrganizationAccessRequestForm(forms.ModelForm):
    class Meta:
        model = OrganizationAccessRequest
        fields = ['organization', 'data_consent']
        widgets = {
            'organization': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nur Organisationen anzeigen, für die der User noch keinen Antrag gestellt hat
        user = kwargs.get('initial', {}).get('user')
        if user:
            existing_requests = OrganizationAccessRequest.objects.filter(
                user=user
            ).values_list('organization_id', flat=True)
            self.fields['organization'].queryset = Organization.objects.exclude(
                id__in=existing_requests
            )

class OrganizationAccessReviewForm(forms.ModelForm):
    class Meta:
        model = OrganizationAccessRequest
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500'
            }),
        }