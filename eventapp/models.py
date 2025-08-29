from authapp.models import Organizations
from django.db import models

# Create your models here.


class EventModel(models.Model):
    title = models.CharField(max_length=100)
    event_url = models.URLField(verbose_name='Event_URL', default='http://127.0.0.1:8000/', blank=True)
    organization = models.ForeignKey(Organizations, related_name='events', on_delete=models.PROTECT, blank=True, null=True) # Organisation kann nicht gelöscht werden, wenn es events gibt.

    

