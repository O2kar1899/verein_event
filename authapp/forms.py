from django import forms
from django.contrib.auth.forms import UserCreationForm  # Dieser Import fehlte
from django.contrib.auth.models import User

from .models import Organization, UserProfile


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