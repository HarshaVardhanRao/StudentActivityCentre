from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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
