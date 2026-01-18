from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from events.models import Event, EventRegistration
from users.models import Club

def home(request):

    if request.user.is_authenticated:
        if "SAC_COORDINATOR" in request.user.roles:
            return redirect('admin-dashboard-template')
    
        return redirect('student-dashboard')

    # Get upcoming and completed events for public display
    now = timezone.now()
    
    # Upcoming events (only approved events that haven't started yet)
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status='APPROVED'
    ).select_related('club').order_by('date_time')[:6]
    
    # Add registration counts to upcoming events for display
    for event in upcoming_events:
        event.registration_count = EventRegistration.objects.filter(event=event).count()
    
    # Completed events (events that have finished)
    completed_events = Event.objects.filter(
        date_time__lt=now,
        status='COMPLETED'
    ).select_related('club').order_by('-date_time')[:6]
    
    # Get some club information for display
    clubs = Club.objects.all()[:8]
    
    # Statistics for the homepage (public view - only approved events)
    stats = {
        'total_events': Event.objects.filter(status='APPROVED').count(),
        'total_clubs': Club.objects.count(),
        'upcoming_events_count': upcoming_events.count(),
        'completed_events_count': completed_events.count(),
    }
    
    context = {
        'upcoming_events': upcoming_events,
        'completed_events': completed_events,
        'clubs': clubs,
        'stats': stats,
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')