from django.shortcuts import render

# templates view
from django.views.generic import TemplateView


# Create your views here.
class StartingPageView(TemplateView):
    template_name = 'startapp/start.html'