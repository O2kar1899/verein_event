from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordChangeView
from django.urls import path

from . import views

app_name = 'authapp'

urlpatterns = [
     path('', views.IndexView.as_view(),name='auth-start'),
     path('registrieren/', views.user_registrieren, name='registrieren'),
     path('bestätigen/<uidb64>/<token>/', views.konto_bestaetigen, name='konto_bestaetigen'),
     path('api/check-username', views.check_username, name='check_username'),
     path("aktivieren/<uidb64>/<token>/", views.konto_bestaetigen, name="konto_bestaetigen"),
     path('login/', views.LoginSeiteView.as_view(), name='login'),
     path("logout", auth_views.LogoutView.as_view(next_page='startapp:starting-page'), name='logout'), 
     path("passwort-aendern/", PasswordChangeView.as_view(template_name="authapp/passwort_aendern.html"),name="passwort_aendern"),
     path("passwort-geaendert/", auth_views.PasswordChangeDoneView.as_view(template_name="authapp/passwort_geaendert.html"),
        name="password_change_done",  # WICHTIG: Genau dieser Name wird erwartet!
    ),
     # Passwort zurücksetzen URLs
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
     # Organisationen URLs
    path('organizations/', views.organization_list, name='organization_list'),
    path('organizations/create/', views.create_organization, name='create_organization'),
     # Zugriffsanfragen
    path('request-access/', views.request_organization_access, name='request_access'),
    path('my-access-requests/', views.my_access_requests, name='my_access_requests'),
    path('review-access-requests/', views.review_access_requests, name='review_access_requests'),
    path('review-access-requests/<int:request_id>/', views.review_access_request_detail, name='review_access_request_detail'),
     ]
