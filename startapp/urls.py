from django.urls import path

from . import views

app_name = 'startapp'

urlpatterns = [
    path('', views.StartingPageView.as_view(), name='starting-page')
]
