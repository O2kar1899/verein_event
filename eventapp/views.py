from authapp.models import Organization
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EventForm
from .models import EventModel


@login_required
def create_event(request):
    organizations = Organization.objects.all()
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            # Zur Event-Liste weiterleiten MIT App-Namespace
            return redirect('eventapp:event_list')
    else:
        form = EventForm()
    
    return render(request, 'eventapp/event_form.html', {
        'form': form,
        'organizations': organizations
    })

def event_list(request):
    events = EventModel.objects.all().order_by('-id')
    return render(request, 'eventapp/event_list.html', {'events': events})

def event_detail(request, event_id):
    event = get_object_or_404(EventModel, id=event_id)
    return render(request, 'eventapp/event_detail.html', {'event': event})