from django.urls import path

from . import views

app_name = 'eventapp'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.create_event, name='create_event'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/register/', views.event_registration, name='event_registration'),
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    path('organization/<int:organization_id>/registrations/', 
         views.organization_event_registrations, 
         name='organization_registrations'),
]