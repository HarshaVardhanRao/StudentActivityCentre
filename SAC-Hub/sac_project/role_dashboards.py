from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from events.models import Event
from users.models import Notification

@login_required
def club_coordinator_dashboard(request):
    return render(request, "club_coordinator_dashboard.html")


@login_required
def svp_dashboard(request):
    return render(request, "svp_dashboard.html")

@login_required
def secretary_dashboard(request):
    return render(request, "secretary_dashboard.html")

@login_required
def treasurer_dashboard(request):
    return render(request, "treasurer_dashboard.html")

@login_required
def department_admin_dashboard(request):
    return render(request, "department_admin_dashboard.html")

@login_required
def club_advisor_dashboard(request):
    return render(request, "club_advisor_dashboard.html")

@login_required
def event_organizer_dashboard(request):
    return render(request, "event_organizer_dashboard.html")

@login_required
def student_volunteer_dashboard(request):
    return render(request, "student_volunteer_dashboard.html")

@login_required
def faculty_dashboard(request):
    return render(request, "faculty_dashboard.html")

@login_required
def admin_dashboard(request):
    # Check if user has admin permissions
    if 'ADMIN' not in (request.user.roles or []) and 'SAC_COORDINATOR' not in (request.user.roles or []):
        return render(request, "admin_dashboard.html", {
            'error_message': 'You do not have permission to access this dashboard.'
        })
    
    # Get dashboard data
    pending_event_proposals = Event.objects.filter(status='PENDING').count()
    approved_events = Event.objects.filter(status='APPROVED').count()
    pending_collaborations = 0  # Placeholder for future collaboration feature
    
    # Get recent notifications for this user
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'pending_event_proposals': pending_event_proposals,
        'approved_events': approved_events,
        'pending_collaborations': pending_collaborations,
        'notifications': notifications,
    }
    
    return render(request, "admin_dashboard.html", context)
