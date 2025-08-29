from django.contrib import admin

from .models import EventModel, Organization

# Register your models here.
admin.site.register(Organization)
admin.site.register(EventModel)