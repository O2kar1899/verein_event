# shortcuts
from django.shortcuts import render, redirect, get_object_or_404
# http
from django.http import HttpResponseForbidden, JsonResponse
# urls 
from django.urls import reverse
# utils 
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# contrib
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
# core
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
# views
from django.views import View
from django.views.generic import TemplateView
# models and forms
from .models import User
from .forms import UserForm
# db
from django.db import IntegrityError, transaction
# logging
import logging
logger = logging.getLogger(__name__)



# Create your views here.
class IndexView(TemplateView):
    template_name = 'main/index.html'


# class LoginSeiteView(TemplateView):
#     template_name = 'main/login.html'


class LoginSeiteView(View):
    def get(self, request):
        return render(request, "main/login.html")  # Formular anzeigen

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("starting-page")  # Weiterleitung zur Startseite
        else:
            messages.error(request, "Ungültiger Benutzername oder Passwort.")
            return render(request, "main/login.html")  # Formular mit Fehler anzeigen

def user_registrieren(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():  # Atomare Transaktion
                    anbieter = form.save()
                    sende_bestaetigungs_email(request, )
                    messages.success(request, "Registrierung erfolgreich! Bitte bestätigen Sie Ihre E-Mail.")
                    return redirect("starting-page")
                    
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                logger.error(f"Registrierungsfehler: {str(e)}")
                messages.error(request, "Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.")
        else:
            # Sammle alle Formularfehler
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = UserForm()
    
    return render(request, "main/registrieren.html", {
        "form": form,
        # "existing_usernames": User.objects.values_list('last_name', flat=True),
        # "existing_emails": User.objects.values_list('email', flat=True)
    })

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
        
        # Debug-Ausgabe
        print(f"\n=== DEBUG EMAIL ===\n"
              f"An: {user.email}\n"
              f"Link: {aktivierungs_link}\n"
              f"===============\n")
        
        send_mail(
            subject="Kontobestätigung",
            message=f"Bitte bestätigen Sie Ihren Account: {aktivierungs_link}",
            from_email=None,  # Nutzt DEFAULT_FROM_EMAIL
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


class AnbieterPortalView(View):
    pass

@login_required
def ansprechperson_erstellen(request):
    anbieter = get_object_or_404(Anbieter, user=request.user)

    if request.method == "POST":
        form = AnsprechpersonForm(request.POST)
        if form.is_valid():
            ap = form.save(commit=False)
            ap.anbieter = anbieter  # sichere Zuordnung
            ap.save()
            return redirect('ansprechpersonen_liste')
    else:
        form = AnsprechpersonForm()
    return render(request, "anbieter/ansprechperson_form.html", {"form": form})


@login_required
def ansprechpersonen_liste(request):
    anbieter = get_object_or_404(Anbieter, user=request.user)
    personen = Ansprechperson.objects.filter(anbieter=anbieter)
    return render(request, "anbieter/ansprechpersonen_liste.html", {"personen": personen})


@login_required
def anbieter_bearbeiten(request):
    if hasattr(request.user, "anbieter_user"):
        # eingeloggter Anbieter
        anbieter = request.user.anbieter_user
    else:
        # Prüfen, ob Ansprechperson ist und ob Änderungen erlaubt sind
        try:
            ansprechperson = Ansprechperson.objects.get(email=request.user.email)
            anbieter = ansprechperson.anbieter
            if not anbieter.allow_edit_by_ansprechpersonen:
                return HttpResponseForbidden("Keine Berechtigung zum Bearbeiten.")
        except Ansprechperson.DoesNotExist:
            return HttpResponseForbidden("Keine Berechtigung.")

    
