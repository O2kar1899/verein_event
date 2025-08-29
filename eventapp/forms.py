from django import forms

from .models import EventModel


class EventForm(forms.ModelForm):
    class Meta:
        model = EventModel
        fields = ['title', 'event_url', 'organization']