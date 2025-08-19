from django.shortcuts import render
from django.views.generic import DetailView, FormView, ListView

# Create your views here.

class EvenListView(ListView):
    pass

class EventDetailView(DetailView):
    pass

class EventCreateView(FormView):
    pass