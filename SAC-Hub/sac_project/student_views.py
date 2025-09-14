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
    if "CLUB_COORDINATOR" in user_roles:
        dashboards.append({"name": "Club Coordinator Dashboard", "url": "/api/dashboard/club-coordinator/"})
    if "EVENT_ORGANIZER" in user_roles:
        dashboards.append({"name": "Event Organizer Dashboard", "url": "/api/dashboard/club-coordinator/"})
    if "SAC_COORDINATOR" in user_roles:
        dashboards.append({"name": "SAC Dashboard", "url": "/api/dashboard/sac/"})
    if "DEPARTMENT_ADMIN" in user_roles:
        dashboards.append({"name": "Department Admin Dashboard", "url": "/api/dashboard/department-admin/"})
    if "PRESIDENT" in user_roles:
        dashboards.append({"name": "President Dashboard", "url": "/api/dashboard/president/"})
    if "SVP" in user_roles:
        dashboards.append({"name": "SVP Dashboard", "url": "/api/dashboard/svp/"})
    if "SECRETARY" in user_roles or "TREASURER" in user_roles:
        dashboards.append({"name": "Secretary/Treasurer Dashboard", "url": "/api/dashboard/secretary-treasurer/"})
    if "CLUB_ADVISOR" in user_roles:
        dashboards.append({"name": "Club Advisor Dashboard", "url": "/api/dashboard/club-advisor/"})
    return render(request, "student_dashboard.html", {
        "ongoing_events": ongoing_events,
        "finished_events": finished_events,
        "notices": notices,
        "contacts": contacts,
        "clubs": clubs,
        "departments": departments,
        "dashboards": dashboards,
    })
