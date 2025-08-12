from django.urls import path
from django.contrib.auth.views import  PasswordChangeView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
     path('', views.IndexView.as_view(), 
          name='starting-page'),
     # path('anbieter-portal/', views.AnbieterPortalView.as_view(),
     #      name='anbieter-portal'),

     path('registrieren/', views.user_registrieren,
         name='registrieren'),

     path('bestätigen/<uidb64>/<token>/', views.konto_bestaetigen, name='konto_bestaetigen'),
     path('api/check-username', views.check_username, name='check_username'),
     path("aktivieren/<uidb64>/<token>/", 
          views.konto_bestaetigen, 
          name="konto_bestaetigen"),
     path('login/', 
          views.LoginSeiteView.as_view(), 
          name='login'),
     path("logout/", 
          auth_views.LogoutView.as_view(), name='logout'),
     path("passwort-aendern/", 
          PasswordChangeView.as_view(template_name="authapp/passwort_aendern.html"), 
          name="passwort_aendern"),
     path(
        "passwort-geaendert/",
        auth_views.PasswordChangeDoneView.as_view(template_name="authapp/passwort_geaendert.html"),
        name="password_change_done",  # WICHTIG: Genau dieser Name wird erwartet!
    ),
     
     # Passwort zurücksetzen URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

     ]
