import logging

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import TemplateView

from .forms import OrganizationForm, UserProfileForm
from .models import Organization, UserProfile

logger = logging.getLogger(__name__)

class IndexView(TemplateView):
    template_name = 'authapp/index.html'


class LoginSeiteView(View):
    def get(self, request):
        return render(request, "authapp/login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember-me")  # Checkbox-Status (None wenn nicht angeklickt)
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            
            # "Angemeldet bleiben" Funktionalität
            if remember_me:
                # Session für 2 Wochen behalten (1209600 Sekunden)
                request.session.set_expiry(1209600)
            else:
                # Session endet wenn Browser geschlossen wird
                request.session.set_expiry(0)
            
            return redirect("startapp:starting-page")
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
                    #return redirect("starting-page")
                    
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
    
    return render(request, "./authapp/registrieren.html", {"form": form})

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
def create_organization(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save()
            messages.success(request, f'Organisation "{organization.name}" wurde erfolgreich erstellt!')
            return redirect('authapp:organization_list')  # Sie müssen diese URL noch definieren
    else:
        form = OrganizationForm()
    
    return render(request, 'authapp/organization.html', {
        'form': form,
        'title': 'Organisation erstellen'
    })

def organization_list(request):
    organizations = Organization.objects.all()
    return render(request, 'authapp/organization_list.html', {
        'organizations': organizations,
        'title': 'Organisationen'
    })