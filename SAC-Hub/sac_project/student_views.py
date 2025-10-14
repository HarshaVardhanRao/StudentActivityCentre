from django.shortcuts import render
from events.models import Event
from users.models import Notification, Club, Department, User
from django.utils import timezone
from django.db.models import Q

def student_dashboard(request):
    now = timezone.now()
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
    if "CLUB_COORDINATOR" in user_roles:
        coordinated_clubs = request.user.coordinated_clubs.all()
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
    
    if "DEPARTMENT_ADMIN" in user_roles:
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
    return render(request, "student_dashboard.html", {
        "ongoing_events": ongoing_events,
        "finished_events": finished_events,
        "notices": notices,
        "contacts": contacts,
        "clubs": clubs,
        "departments": departments,
        "dashboards": dashboards,
    })
