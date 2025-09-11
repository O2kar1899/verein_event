from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    def __str__(self) -> str:
        return self.name
   


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    organizations = models.ManyToManyField(
        Organization,
        blank=True,  # Erlaubt leere Zuordnung
        related_name='members'  # Verein.members.all() gibt alle User
    )

    def __str__(self) -> str:
        return self.user.username

class OrganizationAccessRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ausstehend'),
        ('approved', 'Genehmigt'),
        ('rejected', 'Abgelehnt'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_requests')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='access_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    data_consent = models.BooleanField(
        default=False,
        verbose_name='Ich stimme zu, dass meine Daten an die Organisation übermittelt werden'
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    
    class Meta:
        unique_together = ['user', 'organization']
    
    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.status})"




@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Erstellt ein UserProfile nur wenn der User neu erstellt wurde.
    """
    if created:
        # Nur bei neuen Usern ein UserProfile erstellen
        UserProfile.objects.get_or_create(user=instance)