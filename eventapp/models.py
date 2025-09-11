# eventapp/models.py - Schritt 1: Nur created_by Feld hinzufügen
from authapp.models import Organization
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class EventModel(models.Model):
    title = models.CharField(max_length=100, verbose_name='Titel')
    event_url = models.URLField(verbose_name='Event-URL', default='http://127.0.0.1:8000/', blank=True)
    organization = models.ForeignKey(Organization, related_name='events', on_delete=models.PROTECT, blank=True, null=True, verbose_name='Organisation')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Erstellt von', null=True, blank=True)  # Neues Feld
    description = models.TextField(verbose_name='Beschreibung', blank=True)
    location = models.CharField(max_length=200, verbose_name='Ort', blank=True)
    target_group = models.CharField(max_length=200, verbose_name='Zielgruppe', blank=True)
    start_date = models.DateTimeField(verbose_name='Startdatum')
    end_date = models.DateTimeField(verbose_name='Enddatum', blank=True, null=True)
    is_public = models.BooleanField(default=True, verbose_name='Öffentlich')
    registration_required = models.BooleanField(default=False, verbose_name='Registrierung erforderlich')
    max_participants = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        verbose_name='Maximale Teilnehmerzahl',
        help_text='Optional: Maximale Anzahl an Teilnehmern für dieses Event'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Erstellt am')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Geändert am')
    
    def __str__(self):
        return self.title
    
    def available_spots(self):
        """Berechnet die verfügbaren Plätze"""
        if self.max_participants is None:
            return None
        registered = self.registrations.count() # type: ignore
        return max(0, self.max_participants - registered)
    
    def is_full(self):
        """Prüft ob das Event ausgebucht ist"""
        if self.max_participants is None:
            return False
        return self.registrations.count() >= self.max_participants # type: ignore
    
    def creator_has_organization_access(self):
        """Prüft ob der Ersteller Zugriff auf die gewählte Organisation hat"""
        if not self.organization:
            return True  # Kein Problem wenn keine Organisation gewählt
        
        try:
            from authapp.models import UserProfile
            user_profile = UserProfile.objects.get(user=self.created_by)
            return self.organization in user_profile.organizations.all()
        except UserProfile.DoesNotExist:
            return False
    
    @property
    def organization_access_status(self):
        """Gibt den Status der Organisationsberechtigung zurück"""
        if not self.organization:
            return "no_org"  # Keine Organisation gewählt
        elif self.creator_has_organization_access():
            return "authorized"  # Berechtigt
        else:
            return "unauthorized"  # Nicht berechtigt


class EventRegistration(models.Model):
    event = models.ForeignKey(EventModel, on_delete=models.CASCADE, related_name='registrations')
    first_name = models.CharField(max_length=100, verbose_name='Vorname')
    last_name = models.CharField(max_length=100, verbose_name='Nachname')
    email = models.EmailField(verbose_name='E-Mail-Adresse')
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name='Anmeldedatum')
    
    class Meta:
        unique_together = ['event', 'email']  # Verhindert doppelte Anmeldungen
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.event.title}"