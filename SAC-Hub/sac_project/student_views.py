from django.shortcuts import redirect
from django.shortcuts import render
from events.models import Event
from users.models import Notification, Club, Department, User
from django.utils import timezone
from django.db.models import Q

def student_dashboard(request):
    now = timezone.now()
    # Upcoming events: future dates with APPROVED status
    upcoming_events = Event.objects.filter(date_time__gt=now, status="APPROVED").order_by('date_time')[:6]
    # Ongoing events: current or past with PENDING or APPROVED status
    ongoing_events = Event.objects.filter(date_time__lte=now, status__in=["PENDING", "APPROVED"]).order_by('-date_time')
    finished_events = Event.objects.filter(date_time__lt=now, status="COMPLETED").order_by('-date_time')
    notices = Notification.objects.filter(user__isnull=True).order_by('-created_at')[:10]  # Global notices
    contacts = User.objects.filter(
        Q(roles__contains=["SAC_COORDINATOR"]) |
        Q(roles__contains=["PRESIDENT"]) |
        Q(roles__contains=["SVP"]) |
        Q(roles__contains=["SECRETARY"]) |
        Q(roles__contains=["TREASURER"]) |
        Q(roles__contains=["CLUB_ADVISOR"]) |
        Q(roles__contains=["DEPARTMENT_ADMIN"])
    ).distinct()
    clubs = Club.objects.all()
    departments = Department.objects.all()
    # Dashboard switcher logic
    user_roles = []
    if request.user.is_authenticated:
        user_roles = request.user.roles if isinstance(request.user.roles, list) else []
    dashboards = []
    
    # Check if user is a club coordinator
    if "CLUB_COORDINATOR" in user_roles or "CO_COORDINATOR" in user_roles:
        coordinated_clubs = request.user.coordinated_clubs.all()
        print("Yes")
        return redirect('club_detail', club_id=coordinated_clubs.first().id)
        if coordinated_clubs.exists():
            club_names = ", ".join([club.name for club in coordinated_clubs[:2]])
            if coordinated_clubs.count() > 2:
                club_names += f" and {coordinated_clubs.count() - 2} more"
            dashboards.append({
                "name": f"Club Coordinator Dashboard ({club_names})", 
                "url": "/dashboard/club-coordinator/",
                "icon": "bi bi-people",
                "description": f"Manage {coordinated_clubs.count()} club(s)"
            })
    
    if "EVENT_ORGANIZER" in user_roles:
        dashboards.append({
            "name": "Event Organizer Dashboard", 
            "url": "/dashboard/event-organizer/",
            "icon": "bi bi-calendar-event",
            "description": "Manage events and activities"
        })
    
    if "SAC_COORDINATOR" in user_roles or "ADMIN" in user_roles:
        dashboards.append({
            "name": "SAC Admin Dashboard", 
            "url": "/dashboard/admin/",
            "icon": "bi bi-gear",
            "description": "Oversee all student activities and approve events"
        })
    
    if "DEPARTMENT_ADMIN" in user_roles or "DEPARTMENT_VP" in user_roles:
        dashboards.append({
            "name": "Department Admin Dashboard", 
            "url": "/dashboard/department-admin/",
            "icon": "bi bi-building",
            "description": "Manage department activities"
        })
    
    if "PRESIDENT" in user_roles:
        dashboards.append({
            "name": "President Dashboard", 
            "url": "/dashboard/president/",
            "icon": "bi bi-award",
            "description": "Executive oversight and decisions"
        })
    
    if "SVP" in user_roles:
        dashboards.append({
            "name": "SVP Dashboard", 
            "url": "/dashboard/svp/",
            "icon": "bi bi-star",
            "description": "Strategic planning and review"
        })
    
    if "SECRETARY" in user_roles or "TREASURER" in user_roles:
        role_name = "Secretary" if "SECRETARY" in user_roles else "Treasurer"
        dashboards.append({
            "name": f"{role_name} Dashboard", 
            "url": "/dashboard/secretary/" if "SECRETARY" in user_roles else "/dashboard/treasurer/",
            "icon": "bi bi-journal-text" if "SECRETARY" in user_roles else "bi bi-calculator",
            "description": "Administrative and financial management"
        })
    
    if "CLUB_ADVISOR" in user_roles:
        advised_clubs = request.user.advised_clubs.all()
        dashboards.append({
            "name": "Club Advisor Dashboard", 
            "url": "/dashboard/club-advisor/",
            "icon": "bi bi-person-check",
            "description": f"Advise {advised_clubs.count()} club(s)"
        })

    if "STUDENT_VOLUNTEER" in user_roles:
        dashboards.append({
            "name": "Student Volunteer Dashboard", 
            "url": "/dashboard/student-volunteer/",
            "icon": "bi bi-hand-thumbs-up",
            "description": "Volunteer activities and tasks"
        })

    if "FACULTY" in user_roles:
        dashboards.append({
            "name": "Faculty Dashboard", 
            "url": "/dashboard/faculty/",
            "icon": "bi bi-mortarboard",
            "description": "Faculty oversight and activities"
        })
    # Calculate stats
    my_clubs_count = request.user.clubs.count() if request.user.is_authenticated else 0
    events_attended_count = 0
    
    # Fetch user-specific data
    my_events = []
    my_notifications = []
    registered_events = []
    attended_events = []
    upcoming_registered_events = []
    
    if request.user.is_authenticated:
        from events.models import EventRegistration
        from attendance.models import Attendance
        
        # Stats: Count sessions where student was PRESENT
        events_attended_count = Attendance.objects.filter(student=request.user, status='PRESENT').count()
        
        # 1. Fetch ALL registered events (for tab)
        all_registrations = EventRegistration.objects.filter(
            student=request.user,
            status='REGISTERED'
        ).select_related('event').order_by('-registered_at')
        
        registered_events = [
            {
                'event': reg.event,
                'status': 'REGISTERED',
                'get_status_display': 'Registered',
                'sort_date': reg.event.date_time
            }
            for reg in all_registrations
        ]
        
        # 2. Fetch upcoming registered events (future dates, APPROVED status)
        upcoming_registrations = EventRegistration.objects.filter(
            student=request.user,
            event__date_time__gt=now,
            event__status='APPROVED',
            status='REGISTERED'
        ).select_related('event').order_by('event__date_time')
        
        upcoming_registered_events = [
            {
                'event': reg.event,
                'status': 'REGISTERED',
                'get_status_display': 'Registered',
                'sort_date': reg.event.date_time
            }
            for reg in upcoming_registrations
        ]
        
        # 3. Fetch events user attended (PRESENT)
        attendances = Attendance.objects.filter(
            student=request.user,
            status='PRESENT'
        ).select_related('session__event').order_by('-timestamp')
        
        attended_events = [
            {
                'event': att.session.event,
                'status': 'PRESENT',
                'get_status_display': 'Attended',
                'sort_date': att.session.event.date_time
            }
            for att in attendances if att.session and att.session.event
        ]
        
        # 4. Combine and Deduplicate (Prioritize Attendance) for legacy my_events
        events_map = {}
        
        # Add registrations first
        for item in registered_events:
             events_map[item['event'].id] = item
             
        # Add/Overwrite with Attendance
        for item in attended_events:
            events_map[item['event'].id] = item
        
        # 5. Sort by date descending (Newest/Future first)
        my_events = sorted(events_map.values(), key=lambda x: x['sort_date'], reverse=True)
        
        my_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    is_sac_admin = "SAC_COORDINATOR" in user_roles or "ADMIN" in user_roles

    context = {
        'page_title': 'Student Dashboard',
        'stats': {
            'total_clubs': my_clubs_count, 
            'pending_events': upcoming_events.count(),
            'total_users': events_attended_count,
            'is_sac_admin': is_sac_admin, # Flag for template to switch labels
        },
        'dashboard_events': upcoming_events,
        'dashboard_clubs': request.user.clubs.all() if request.user.is_authenticated else [],
        'dashboard_members': [], # Not applicable for students
        'upcoming_events': upcoming_events,
        'ongoing_events': ongoing_events,
        'finished_events': finished_events,
        'notices': notices,
        'my_notifications': my_notifications,
        'my_events': my_events,
        'registered_events': registered_events,
        'attended_events': attended_events,
        'upcoming_registered_events': upcoming_registered_events,
        'contacts': contacts,
        'clubs': clubs,
        'departments': departments,
        'dashboards': dashboards,
    }
    return render(request, "dashboard/unified_dashboard.html", context)
