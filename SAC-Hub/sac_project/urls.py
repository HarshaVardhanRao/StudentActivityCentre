"""
URL configuration for sac_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin

from django.urls import path, include
from users.admin_bulk_upload import bulk_upload_view
from .dashboard_views import (
    SACDashboardView, ClubCoordinatorDashboardView, DepartmentAdminDashboardView,
    PresidentDashboardView, SVPDashboardView, SecretaryTreasurerDashboardView, ClubAdvisorDashboardView
)
from .student_views import student_dashboard
from .role_dashboards import (
    club_coordinator_dashboard, svp_dashboard, secretary_dashboard,
    treasurer_dashboard, department_admin_dashboard, club_advisor_dashboard, event_organizer_dashboard,
    student_volunteer_dashboard, faculty_dashboard, admin_dashboard
)
from .auth_views import login_view, logout_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("", student_dashboard, name="student-dashboard"),
    path("admin/", admin.site.urls),
    path("bulk-upload/", bulk_upload_view, name="bulk-upload"),
    path("api/", include("users.api_urls")),
    path("api/", include("events.api_urls")),
    path("api/", include("attendance.api_urls")),
    path("api/", include("calendar_app.api_urls")),
    path("api/dashboard/sac/", SACDashboardView.as_view(), name="sac-dashboard"),
    path("api/dashboard/club-coordinator/", ClubCoordinatorDashboardView.as_view(), name="club-coordinator-dashboard"),
    path("api/dashboard/department-admin/", DepartmentAdminDashboardView.as_view(), name="department-admin-dashboard"),
    path("api/dashboard/president/", PresidentDashboardView.as_view(), name="president-dashboard"),
    path("api/dashboard/svp/", SVPDashboardView.as_view(), name="svp-dashboard"),
    path("api/dashboard/secretary-treasurer/", SecretaryTreasurerDashboardView.as_view(), name="secretary-treasurer-dashboard"),
    path("api/dashboard/club-advisor/", ClubAdvisorDashboardView.as_view(), name="club-advisor-dashboard"),

    # Role-based dashboard template views
    path("dashboard/club-coordinator/", club_coordinator_dashboard, name="club-coordinator-dashboard-template"),
    path("dashboard/svp/", svp_dashboard, name="svp-dashboard-template"),
    path("dashboard/secretary/", secretary_dashboard, name="secretary-dashboard-template"),
    path("dashboard/treasurer/", treasurer_dashboard, name="treasurer-dashboard-template"),
    path("dashboard/department-admin/", department_admin_dashboard, name="department-admin-dashboard-template"),
    path("dashboard/club-advisor/", club_advisor_dashboard, name="club-advisor-dashboard-template"),
    path("dashboard/event-organizer/", event_organizer_dashboard, name="event-organizer-dashboard-template"),
    path("dashboard/student-volunteer/", student_volunteer_dashboard, name="student-volunteer-dashboard-template"),
    path("dashboard/faculty/", faculty_dashboard, name="faculty-dashboard-template"),
    path("dashboard/admin/", admin_dashboard, name="admin-dashboard-template"),
]
