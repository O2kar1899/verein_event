from authapp.models import Organization
from django.db import models
from django.utils import timezone


class EventModel(models.Model):
    title = models.CharField(max_length=100)
    event_url = models.URLField(verbose_name='Event_URL', default='http://127.0.0.1:8000/', blank=True)
    organization = models.ForeignKey(Organization, related_name='events', on_delete=models.PROTECT, blank=True, null=True)
    description = models.TextField(verbose_name='Beschreibung', blank=True)
    location = models.CharField(max_length=200, verbose_name='Ort', blank=True)
    target_group = models.CharField(max_length=200, verbose_name='Zielgruppe', blank=True)
    start_date = models.DateTimeField(verbose_name='Startdatum')
    end_date = models.DateTimeField(verbose_name='Enddatum', blank=True, null=True)
    is_public = models.BooleanField(default=True, verbose_name='Öffentlich')
    
    created_at = models.DateTimeField(verbose_name='Erstellt am', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Geändert am', auto_now=True)
    
    def __str__(self):
        return self.title