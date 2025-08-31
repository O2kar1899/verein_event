from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=150)
    organization_url = models.URLField(verbose_name='Orga_URL')
    street = models.CharField(max_length=100, null=True, blank=True)
    post_code = models.CharField(
        max_length=5,  # DE/AT: 5-stellig, CH: 4-stellig (ggf. anpassen)
        validators=[
            RegexValidator(
                regex=r'^\d{5}$',  # für deutsche Postleitzahlen
                message="Die PLZ muss aus 5 Ziffern bestehen."
            )
        ],
        verbose_name="Postleitzahl"
        )
    city = models.CharField(max_length=100, null=True, blank=True)
    authenticity_checked = models.BooleanField(default=False)
   


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    vereine = models.ManyToManyField(
        Organization,
        blank=True,  # Erlaubt leere Zuordnung
        related_name='mitglieder'  # Verein.mitglieder.all() gibt alle User
    )

    