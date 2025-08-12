from django.db import models
from django.contrib.auth.models import User


class Verein(models.Model):
    name = models.CharField(max_length=100)
    straße = models.CharField(max_length=255, blank=True, null=True)
    plz = models.CharField(max_length=10, blank=True, null=True)
    ort = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    
    beschreibung = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name



class Veranstaltung(models.Model):
    titel = models.CharField(max_length=150),

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    vereine = models.ManyToManyField(
        Verein, 
        blank=True,  # Erlaubt leere Zuordnung
        related_name='mitglieder'  # Verein.mitglieder.all() gibt alle User
    )

    def __str__(self):
        vereine_names = ", ".join([v.name for v in self.vereine.all()])
        return f"{self.user.get_full_name()} ({vereine_names if vereine_names else 'Kein Verein'})"