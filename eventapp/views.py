from django.shortcuts import render
from django.views.generic import ListView, DetailView, FormView

# Create your views here.

class EvenListView(ListView):
    pass

class EventDetailView(DetailView):
    pass

class EventCreateView(FormView)
    pass