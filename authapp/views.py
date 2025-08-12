from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.views import View
from django.views.generic import TemplateView
from django.db import transaction
from .models import UserProfile, Verein
from .forms import UserProfileForm
import logging

logger = logging.getLogger(__name__)

class IndexView(TemplateView):
    template_name = 'authapp/index.html'

class LoginSeiteView(View):
    def get(self, request):
        return render(request, "authapp/login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("starting-page")
        else:
            messages.error(request, "Ungültiger Benutzername oder Passwort.")
            return render(request, "authapp/login.html")

def user_registrieren(request):
    if request.method == "POST":
        form = UserProfileForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    sende_bestaetigungs_email(request, user)
                    messages.success(request, "Registrierung erfolgreich! Bitte bestätigen Sie Ihre E-Mail.")
                    return redirect("starting-page")
                    
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                logger.error(f"Registrierungsfehler: {str(e)}")
                messages.error(request, "Ein unerwarteter Fehler ist aufgetreten.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = UserProfileForm()
    
    return render(request, "authapp/registrieren.html", {"form": form})

def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'exists': exists})

def sende_bestaetigungs_email(request, user):
    try:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        aktivierungs_link = request.build_absolute_uri(
            reverse("konto_bestaetigen", kwargs={"uidb64": uid, "token": token})
        )
        
        send_mail(
            subject="Kontobestätigung",
            message=f"Bitte bestätigen Sie Ihren Account: {aktivierungs_link}",
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False
        )
        return True
    except Exception as e:
        logger.error(f"E-Mail-Fehler: {str(e)}", exc_info=True)
        raise ValidationError("Bestätigungs-E-Mail konnte nicht gesendet werden.")

def konto_bestaetigen(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Konto erfolgreich bestätigt! Sie können sich jetzt einloggen.')
        return redirect('login')
    else:
        messages.error(request, 'Ungültiger oder abgelaufener Bestätigungslink.')
        return redirect('registrieren')

@login_required
def vereins_verwaltung(request):
    user_profile = request.user.profile
    vereine = user_profile.vereine.all()
    return render(request, "authapp/vereins_verwaltung.html", {
        'vereine': vereine,
        'user_profile': user_profile
    })

@login_required
def verein_hinzufuegen(request):
    if request.method == "POST":
        verein_id = request.POST.get('verein_id')
        try:
            verein = Verein.objects.get(id=verein_id)
            request.user.profile.vereine.add(verein)
            messages.success(request, f"Sie wurden dem Verein {verein.name} hinzugefügt.")
        except Verein.DoesNotExist:
            messages.error(request, "Verein nicht gefunden.")
        return redirect('vereins_verwaltung')
    
    verfuegbare_vereine = Verein.objects.exclude(mitglieder=request.user.profile)
    return render(request, "authapp/verein_hinzufuegen.html", {
        'verfuegbare_vereine': verfuegbare_vereine
    })

@login_required
def verein_entfernen(request, verein_id):
    try:
        verein = Verein.objects.get(id=verein_id)
        request.user.profile.vereine.remove(verein)
        messages.success(request, f"Sie wurden aus dem Verein {verein.name} entfernt.")
    except Verein.DoesNotExist:
        messages.error(request, "Verein nicht gefunden.")
    return redirect('vereins_verwaltung')