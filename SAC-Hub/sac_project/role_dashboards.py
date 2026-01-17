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
        'dashboard_events': upcoming_events,
        'dashboard_clubs': coordinator_clubs,
        'dashboard_members': dashboard_members,
        'users': dashboard_members,
        'completed_events': completed_events,
        'coordinator_clubs': coordinator_clubs,
        'club_events': club_events_count,
        'pending_approvals': pending_approvals_count,
        'participant_lists': participant_count,
        'coordinator_club': coordinator_club,
        'notifications': notifications,
        'upcoming_events': upcoming_events,
        'my_notifications': notifications,
        'my_events': [],
        'previous_reports': [],
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
        'upcoming_events': upcoming_events,
        'my_notifications': [],
        'my_events': upcoming_events,
        'previous_reports': [],
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
        'upcoming_events': upcoming_events,
        'my_notifications': [],
        'my_events': upcoming_events,
        'previous_reports': [],
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
        'upcoming_events': upcoming_events,
        'my_notifications': [],
        'my_events': upcoming_events,
        'previous_reports': [],
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
        'upcoming_events': upcoming_events,
        'my_notifications': [],
        'my_events': upcoming_events,
        'previous_reports': [],
    }
    return render(request, "dashboard/unified_dashboard.html", context)

@login_required
def club_advisor_dashboard(request):
    now = timezone.now()
    from clubs.models import ClubReport
    from events.models import EventReport
    
    advised_clubs = request.user.advised_clubs.all()
    upcoming_events = Event.objects.filter(
        club__in=advised_clubs,
        date_time__gt=now,
        status="APPROVED"
    ).order_by('date_time')[:6]
    
    # Get both ClubReport and EventReport
    previous_reports = ClubReport.objects.filter(club__in=advised_clubs).order_by('-created_at')[:5]
    event_reports = EventReport.objects.filter(
        event__club__in=advised_clubs
    ).order_by('-created_at')[:5]

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
        'event_reports': event_reports,
        'show_report_submission': True,
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
    from datetime import timedelta
    
    from clubs.models import ClubReport
    from events.models import EventReport
    
    # Check if user has admin permissions
    if 'ADMIN' not in (request.user.roles or []) and 'SAC_COORDINATOR' not in (request.user.roles or []):
        return render(request, "admin_dashboard.html", {
            'error_message': 'You do not have permission to access this dashboard.'
        })
    
    # Events categorization
    pending_events = Event.objects.filter(status='PENDING').order_by('date_time')
    approved_events = Event.objects.filter(status='APPROVED').order_by('-date_time')
    completed_events = Event.objects.filter(status='COMPLETED').order_by('-date_time')
    rejected_events = Event.objects.filter(status='REJECTED').order_by('-date_time')
    
    # Resource requests (events with resources specified)
    resource_requests = Event.objects.exclude(resources='').exclude(resources__isnull=True).filter(status='PENDING')
    
    # Reports - Both ClubReport and EventReport
    pending_reports = ClubReport.objects.filter(status='PENDING')
    pending_event_reports = EventReport.objects.filter(status='PENDING').select_related('event', 'submitted_by', 'approved_by')
    approved_event_reports = EventReport.objects.filter(status='APPROVED').select_related('event', 'submitted_by', 'approved_by')
    
    # Calculate analytics
    total_events = Event.objects.count()
    all_attendances = Attendance.objects.all()
    total_attendees = all_attendances.count()
    avg_attendance = round(total_attendees / total_events) if total_events > 0 else 0
    
    # Success rate (completed + approved / total)
    success_count = completed_events.count() + approved_events.count()
    success_rate = round((success_count / total_events) * 100) if total_events > 0 else 0
    
    # Statistics
    stats = {
        'total_users': User.objects.count(),
        'total_clubs': Club.objects.count(),
        'total_departments': Department.objects.count(),
        'total_events': total_events,
        'pending_events': pending_events.count(),
        'approved_events': approved_events.count(),
        'completed_events': completed_events.count(),
        'rejected_events': rejected_events.count(),
        'total_attendance_records': Attendance.objects.count(),
        'total_calendar_entries': CalendarEntry.objects.count(),
        'pending_reports': pending_reports.count(),
        'pending_event_reports': pending_event_reports.count(),
        'is_sac_admin': True,
        'avg_attendance': avg_attendance,
        'success_rate': success_rate,
        'total_attendees': total_attendees,
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
        'page_title': 'SAC Coordinator Dashboard',
        'stats': stats,
        'pending_events': pending_events,
        'approved_events': approved_events,
        'completed_events': completed_events,
        'rejected_events': rejected_events,
        'resource_requests': resource_requests,
        'pending_reports': pending_reports,
        'pending_event_reports': pending_event_reports,
        'approved_event_reports': approved_event_reports,
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
        'show_calendar_control': True,
        'show_report_approval': True,
    }
    
    return render(request, "admin_dashboard.html", context)
