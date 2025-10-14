from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

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
    return render(request, "admin_dashboard.html")


@login_required
def dashboard_redirect(request, role):
    """Redirect a generic role string to the appropriate named dashboard template.

    The project stores roles as uppercase constants (e.g. 'PRESIDENT', 'SVP').
    This view normalizes the role and redirects to the template route already
    present in `urls.py`. If no mapping exists, redirect to the main student dashboard.
    """
    role_norm = (role or "").upper()
    mapping = {
        "CLUB_COORDINATOR": "club-coordinator-dashboard-template",
        "EVENT_ORGANIZER": "event-organizer-dashboard-template",
        "SAC_COORDINATOR": "admin-dashboard-template",
        "ADMIN": "admin-dashboard-template",
        "DEPARTMENT_ADMIN": "department-admin-dashboard-template",
        "PRESIDENT": "student-dashboard",  # no specific president template; fallback
        "SVP": "svp-dashboard-template",
        "SECRETARY": "secretary-dashboard-template",
        "TREASURER": "treasurer-dashboard-template",
        "CLUB_ADVISOR": "club-advisor-dashboard-template",
        "STUDENT_VOLUNTEER": "student-volunteer-dashboard-template",
        "FACULTY": "faculty-dashboard-template",
    }

    target_name = mapping.get(role_norm)
    if target_name:
        return redirect(target_name)
    # fallback
    return redirect("student-dashboard")
