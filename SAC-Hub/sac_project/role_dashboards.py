from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from events.models import Event
from users.models import Notification
from django.shortcuts import redirect
from django.utils import timezone

@login_required
def club_coordinator_dashboard(request):
    from users.models import Club, Notification, User
    from events.models import Event
    from attendance.models import Attendance

    # Get clubs this user coordinates
    coordinator_clubs = request.user.coordinated_clubs.all()

    # Basic counts
    club_events_count = Event.objects.filter(club__in=coordinator_clubs).count()
    pending_approvals_count = Event.objects.filter(club__in=coordinator_clubs, status='PENDING').count()
    participant_count = Attendance.objects.filter(session__event__club__in=coordinator_clubs).count()

    coordinator_club = coordinator_clubs.first() if coordinator_clubs.count() == 1 else None

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Get members of clubs this user coordinates
    dashboard_members = User.objects.filter(clubs__in=coordinator_clubs).distinct()
    
    now = timezone.now()
    # Upcoming events: PENDING and APPROVED
    upcoming_events = Event.objects.filter(
        club__in=coordinator_clubs,
        date_time__gt=now,
        status__in=["APPROVED", "PENDING"]
    ).order_by('date_time')
    
    completed_events = Event.objects.filter(
        club__in=coordinator_clubs,
        status="COMPLETED"
    ).order_by('-date_time')

    context = {
        'page_title': 'Club Coordinator Dashboard',
        'stats': {
            'total_clubs': coordinator_clubs.count(),
            'pending_events': pending_approvals_count,
            'total_users': dashboard_members.count(),
        },
        'dashboard_events': upcoming_events, # Main list
        'dashboard_clubs': coordinator_clubs,
        'dashboard_members': dashboard_members,
        'users': dashboard_members, # For Manage Users table compatibility
        'completed_events': completed_events,
        'coordinator_clubs': coordinator_clubs,
        'club_events': club_events_count,
        'pending_approvals': pending_approvals_count,
        'participant_lists': participant_count,
        'coordinator_club': coordinator_club,
        'notifications': notifications,
        'upcoming_events': upcoming_events,
    }
    return render(request, "dashboard/unified_dashboard.html", context)


@login_required
def svp_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    context = {
        'page_title': 'SVP Dashboard',
        'stats': {},
        'dashboard_events': upcoming_events,
        'dashboard_clubs': [],
        'dashboard_members': [],
        'upcoming_events': upcoming_events
    }
    return render(request, "dashboard/unified_dashboard.html", context)

@login_required
def secretary_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    context = {
        'page_title': 'Secretary Dashboard',
        'stats': {},
        'dashboard_events': upcoming_events,
        'dashboard_clubs': [],
        'dashboard_members': [],
        'upcoming_events': upcoming_events
    }
    return render(request, "dashboard/unified_dashboard.html", context)

@login_required
def treasurer_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    context = {
        'page_title': 'Treasurer Dashboard',
        'stats': {},
        'dashboard_events': upcoming_events,
        'dashboard_clubs': [],
        'dashboard_members': [],
        'upcoming_events': upcoming_events
    }
    return render(request, "dashboard/unified_dashboard.html", context)

@login_required
def department_admin_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    context = {
        'page_title': 'Department Admin Dashboard',
        'stats': {},
        'dashboard_events': upcoming_events,
        'dashboard_clubs': [],
        'dashboard_members': [],
        'upcoming_events': upcoming_events
    }
    return render(request, "dashboard/unified_dashboard.html", context)

@login_required
def club_advisor_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    from clubs.models import ClubReport
    advised_clubs = request.user.advised_clubs.all()
    upcoming_events = Event.objects.filter(
        club__in=advised_clubs,
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    
    previous_reports = ClubReport.objects.filter(club__in=advised_clubs).order_by('-created_at')[:5]

    context = {
        'page_title': 'Club Advisor Dashboard',
        'stats': {
            'advised_clubs': advised_clubs.count(),
            'upcoming_events': upcoming_events.count(),
        },
        'dashboard_events': upcoming_events,
        'dashboard_clubs': advised_clubs,
        'dashboard_members': [],
        'upcoming_events': upcoming_events,
        'previous_reports': previous_reports,
        'show_report_submission': True, # Flag to show report submission form
    }
    return render(request, "dashboard/unified_dashboard.html", context)

@login_required
def event_organizer_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    context = {
        'page_title': 'Event Organizer Dashboard',
        'stats': {},
        'dashboard_events': upcoming_events,
        'dashboard_clubs': [],
        'dashboard_members': [],
        'upcoming_events': upcoming_events
    }
    return render(request, "dashboard/unified_dashboard.html", context)

@login_required
def student_volunteer_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    context = {
        'page_title': 'Student Volunteer Dashboard',
        'stats': {},
        'dashboard_events': upcoming_events,
        'dashboard_clubs': [],
        'dashboard_members': [],
        'upcoming_events': upcoming_events
    }
    return render(request, "dashboard/unified_dashboard.html", context)

@login_required
def faculty_dashboard(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    context = {
        'page_title': 'Faculty Dashboard',
        'stats': {},
        'dashboard_events': upcoming_events,
        'dashboard_clubs': [],
        'dashboard_members': [],
        'upcoming_events': upcoming_events
    }
    return render(request, "dashboard/unified_dashboard.html", context)

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
    
    from clubs.models import ClubReport
    
    # Check if user has admin permissions
    if 'ADMIN' not in (request.user.roles or []) and 'SAC_COORDINATOR' not in (request.user.roles or []):
        return render(request, "admin_dashboard.html", {
            'error_message': 'You do not have permission to access this dashboard.'
        })
    
    # Events categorization
    planned_events = Event.objects.filter(status='PENDING').order_by('date_time')
    approved_events = Event.objects.filter(status='APPROVED').order_by('-date_time')[:20]
    completed_events = Event.objects.filter(status='COMPLETED').order_by('-date_time')[:20]
    cancelled_events = Event.objects.filter(status='REJECTED').order_by('-date_time')[:20]
    
    # Resource requests (events with resources specified)
    resource_requests = Event.objects.exclude(resources='').exclude(resources__isnull=True).filter(status='PENDING')
    
    # Reports
    pending_reports = ClubReport.objects.filter(status='PENDING')
    
    # Statistics
    stats = {
        'total_users': User.objects.count(),
        'total_clubs': Club.objects.count(),
        'total_departments': Department.objects.count(),
        'total_events': Event.objects.count(),
        'pending_events': planned_events.count(),
        'approved_events': approved_events.count(),
        'total_attendance_records': Attendance.objects.count(),
        'total_calendar_entries': CalendarEntry.objects.count(),
        'pending_reports': pending_reports.count(),
        'is_sac_admin': True,
    }
    
    # Lists for management
    users = User.objects.all().order_by('-date_joined')[:50]
    clubs = Club.objects.all()
    departments = Department.objects.all()
    events = Event.objects.all().order_by('-created_at')[:20]
    attendances = Attendance.objects.select_related('session', 'session__event', 'student').order_by('-timestamp')[:20]
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
        'page_title': 'SAC Coordinator Dashboard', # Updated title
        'stats': stats,
        'dashboard_events': planned_events, # Default view
        'planned_events': planned_events,
        'approved_events': approved_events,
        'completed_events': completed_events,
        'cancelled_events': cancelled_events,
        'resource_requests': resource_requests,
        'pending_reports': pending_reports,
        'dashboard_clubs': clubs,
        'dashboard_members': users,
        'users': users,
        'clubs': clubs,
        'departments': departments,
        'events': events,
        'attendances': attendances,
        'calendar_entries': calendar_entries,
        'notifications': notifications,
        'upcoming_events': upcoming_events,
        'show_calendar_control': True, # Flag for calendar control
        'show_report_approval': True, # Flag for report approval
    }
    
    return render(request, "dashboard/unified_dashboard.html", context)
