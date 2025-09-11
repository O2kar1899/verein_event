# eventapp/views.py - Schritt 2: Erweiterte Version
from authapp.models import Organization, UserProfile
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render

from .forms_old import EmailLookupForm, EventForm, EventRegistrationForm
from .models import EventModel, EventRegistration


@login_required
def create_event(request):
    print(f"DEBUG VIEW: User = {request.user}")  # <-- Diese Zeile hinzufügen
    if request.method == 'POST':
        form = EventForm(request.POST, user=request.user)
        print(f"DEBUG VIEW: Form erstellt (POST) mit user = {request.user}")
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user  # Creator setzen
            
            # Zusätzliche Validierung: Prüfen ob User für gewählte Organisation berechtigt ist
            if event.organization:
                try:
                    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
                    if event.organization not in user_profile.organizations.all():
                        messages.error(request, 
                                     f"Sie sind nicht für die Organisation '{event.organization.name}' freigeschaltet.")
                        return render(request, 'eventapp/event_form.html', {'form': form})
                except UserProfile.DoesNotExist:
                    messages.error(request, "Profil nicht gefunden. Bitte vervollständigen Sie zunächst Ihr Profil.")
                    return render(request, 'eventapp/event_form.html', {'form': form})
            
            event.save()
            messages.success(request, f"Event '{event.title}' wurde erfolgreich erstellt!")
            return redirect('eventapp:event_list')
    else:
        form = EventForm(user=request.user)
        print(f"DEBUG VIEW: Form erstellt (GET) mit user = {request.user}") 
    
    return render(request, 'eventapp/event_form.html', {'form': form})


def event_list(request):
    events = EventModel.objects.select_related('created_by', 'organization').all().order_by('-created_at')
    return render(request, 'eventapp/event_list.html', {'events': events})


def event_detail(request, event_id):
    event = get_object_or_404(EventModel.objects.select_related('created_by', 'organization'), id=event_id)
    return render(request, 'eventapp/event_detail.html', {'event': event})


def event_registration(request, event_id):
    event = get_object_or_404(EventModel, id=event_id, is_public=True)
    
    if not event.registration_required:
        messages.error(request, "Für dieses Event ist keine Anmeldung erforderlich.")
        return redirect('eventapp:event_detail', event_id=event.id)
    
    if event.is_full():
        messages.error(request, "Dieses Event ist bereits ausgebucht.")
        return redirect('eventapp:event_detail', event_id=event.id)
    
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
                return redirect('eventapp:event_detail', event_id=event.id)
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
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
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