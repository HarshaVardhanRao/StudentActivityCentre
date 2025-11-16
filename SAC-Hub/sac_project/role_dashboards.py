from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from events.models import Event
from users.models import Notification
from django.shortcuts import redirect
from django.utils import timezone

@login_required
def club_coordinator_dashboard(request):
    from users.models import Club, Notification
    from events.models import Event
    from attendance.models import Attendance

    # Get clubs this user coordinates
    coordinator_clubs = request.user.coordinated_clubs.all()

    # Basic counts
    club_events_count = Event.objects.filter(club__in=coordinator_clubs).count()
    pending_approvals_count = Event.objects.filter(club__in=coordinator_clubs, status='PENDING').count()
    participant_count = Attendance.objects.filter(event__club__in=coordinator_clubs).count()

    coordinator_club = coordinator_clubs.first() if coordinator_clubs.count() == 1 else None

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Upcoming events for the coordinator's clubs
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        club__in=coordinator_clubs,
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]

    context = {
        'coordinator_clubs': coordinator_clubs,
        'club_events': club_events_count,
        'pending_approvals': pending_approvals_count,
        'participant_lists': participant_count,
        'coordinator_club': coordinator_club,
        'notifications': notifications,
        'upcoming_events': upcoming_events,
    }
    return render(request, "club_coordinator_dashboard.html", context)


@login_required
def svp_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    return render(request, "svp_dashboard.html", {'upcoming_events': upcoming_events})

@login_required
def secretary_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    return render(request, "secretary_dashboard.html", {'upcoming_events': upcoming_events})

@login_required
def treasurer_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    return render(request, "treasurer_dashboard.html", {'upcoming_events': upcoming_events})

@login_required
def department_admin_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    return render(request, "department_admin_dashboard.html", {'upcoming_events': upcoming_events})

@login_required
def club_advisor_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    return render(request, "club_advisor_dashboard.html", {'upcoming_events': upcoming_events})

@login_required
def event_organizer_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    return render(request, "event_organizer_dashboard.html", {'upcoming_events': upcoming_events})

@login_required
def student_volunteer_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    return render(request, "student_volunteer_dashboard.html", {'upcoming_events': upcoming_events})

@login_required
def faculty_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    return render(request, "faculty_dashboard.html", {'upcoming_events': upcoming_events})

@login_required
def dashboard_redirect(request, role):
    """Redirect to the appropriate dashboard based on user role."""
    role_to_view = {
        'club-coordinator': 'club-coordinator-dashboard-template',
        'svp': 'svp-dashboard-template',
        'secretary': 'secretary-dashboard-template',
        'treasurer': 'treasurer-dashboard-template',
        'department-admin': 'department-admin-dashboard-template',
        'club-advisor': 'club-advisor-dashboard-template',
        'event-organizer': 'event-organizer-dashboard-template',
        'student-volunteer': 'student-volunteer-dashboard-template',
        'faculty': 'faculty-dashboard-template',
        'admin': 'admin-dashboard-template',
    }
    
    view_name = role_to_view.get(role)
    if view_name:
        return redirect(view_name)
    return redirect('home')

@login_required
def admin_dashboard(request):
    from users.models import User, Club, Department
    from attendance.models import Attendance
    from calendar_app.models import CalendarEntry
    
    # Check if user has admin permissions
    if 'ADMIN' not in (request.user.roles or []) and 'SAC_COORDINATOR' not in (request.user.roles or []):
        return render(request, "admin_dashboard.html", {
            'error_message': 'You do not have permission to access this dashboard.'
        })
    
    # Statistics
    stats = {
        'total_users': User.objects.count(),
        'total_clubs': Club.objects.count(),
        'total_departments': Department.objects.count(),
        'total_events': Event.objects.count(),
        'pending_events': Event.objects.filter(status='PENDING').count(),
        'approved_events': Event.objects.filter(status='APPROVED').count(),
        'total_attendance_records': Attendance.objects.count(),
        'total_calendar_entries': CalendarEntry.objects.count(),
    }
    
    # Lists for management
    users = User.objects.all().order_by('-date_joined')[:50]
    clubs = Club.objects.all()
    departments = Department.objects.all()
    events = Event.objects.all().order_by('-created_at')[:20]
    attendances = Attendance.objects.select_related('event', 'student').order_by('-timestamp')[:20]
    calendar_entries = CalendarEntry.objects.select_related('event').order_by('-date_time')[:20]
    
    # Get recent notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Upcoming events
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    
    context = {
        'stats': stats,
        'users': users,
        'clubs': clubs,
        'departments': departments,
        'events': events,
        'attendances': attendances,
        'calendar_entries': calendar_entries,
        'notifications': notifications,
        'upcoming_events': upcoming_events,
    }
    
    return render(request, "admin_dashboard.html", context)
