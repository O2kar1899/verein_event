from authapp.models import Organization, UserProfile
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmailLookupForm, EventForm, EventRegistrationForm
from .models import EventModel, EventRegistration


@login_required
def create_event(request):
    organizations = Organization.objects.all()
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            # Zur Event-Liste weiterleiten MIT App-Namespace
            return redirect('eventapp:event_list')
    else:
        form = EventForm()
    
    return render(request, 'eventapp/event_form.html', {
        'form': form,
        'organizations': organizations
    })

def event_list(request):
    events = EventModel.objects.all().order_by('-id')
    return render(request, 'eventapp/event_list.html', {'events': events})

def event_detail(request, event_id):
    event = get_object_or_404(EventModel, id=event_id)
    return render(request, 'eventapp/event_detail.html', {'event': event})

def event_registration(request, event_id):
    event = get_object_or_404(EventModel, id=event_id, is_public=True)
    
    if not event.registration_required:
        messages.error(request, "Für dieses Event ist keine Anmeldung erforderlich.")
        return redirect('eventapp:event_detail', event_id=event.id) # type: ignore
    
    if event.is_full():
        messages.error(request, "Dieses Event ist bereits ausgebucht.")
        return redirect('eventapp:event_detail', event_id=event.id) # type: ignore
    
    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            
            # Prüfen ob E-Mail bereits registriert ist
            if EventRegistration.objects.filter(event=event, email=registration.email).exists():
                messages.error(request, "Diese E-Mail ist bereits für dieses Event registriert.")
            else:
                registration.save()
                messages.success(request, "Sie haben sich erfolgreich für das Event angemeldet!")
                return redirect('eventapp:event_detail', event_id=event.id) # type: ignore
    else:
        form = EventRegistrationForm()
    
    return render(request, 'eventapp/event_registration.html', {
        'form': form,
        'event': event
    })

def my_registrations(request):
    if request.method == 'POST':
        form = EmailLookupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            registrations = EventRegistration.objects.filter(email=email).select_related('event')
            
            if registrations.exists():
                # E-Mail mit Registrierungen senden
                event_list = "\n".join([
                    f"- {reg.event.title} am {reg.event.start_date.strftime('%d.%m.%Y %H:%M')}"
                    for reg in registrations
                ])
                
                subject = 'Ihre Event-Registrierungen'
                message = f'''Hallo,\n\nSie haben sich für folgende Events registriert:\n\n{event_list}\n\nMit freundlichen Grüßen\nIhr Veranstaltungsteam'''
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                messages.success(request, "Eine E-Mail mit Ihren Registrierungen wurde an Ihre E-Mail-Adresse gesendet.")
            else:
                messages.info(request, "Für diese E-Mail-Adresse wurden keine Registrierungen gefunden.")
            
            return redirect('eventapp:event_list')
    else:
        form = EmailLookupForm()
    
    return render(request, 'eventapp/my_registrations.html', {'form': form})



@login_required
def organization_event_registrations(request, organization_id):
    # Prüfen ob User Zugriff auf diese Organisation hat
    user_profile = UserProfile.objects.get(user=request.user)
    organization = get_object_or_404(Organization, id=organization_id)
    
    if organization not in user_profile.organizations.all():
        messages.error(request, "Sie haben keinen Zugriff auf diese Organisation.")
        return redirect('eventapp:event_list')
    
    # Events der Organisation mit Registrierungen
    events = EventModel.objects.filter(organization=organization).prefetch_related('registrations')
    
    return render(request, 'eventapp/organization_registrations.html', {
        'organization': organization,
        'events': events,
        'title': f'Registrierungen - {organization.name}'
    })


