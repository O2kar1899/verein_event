from django.db import models
from django.core.validators import RegexValidator

# Create your models here.
class OrganizationsModel(models.Model):
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
    

class EventModel(models.Model):
    title = models.CharField(max_length=100)
    event_url = models.URLField(verbose_name='Event_URL')
    organization = models.ForeignKey(OrganizationsModel, related_name='events', on_delete=models.PROTECT) # Organisation kann nicht gelöscht werden, wenn es events gibt.

    

