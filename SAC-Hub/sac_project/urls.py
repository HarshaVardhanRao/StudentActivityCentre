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
    PresidentDashboardView, SVPDashboardView, SecretaryDashboardView, TreasurerDashboardView, ClubAdvisorDashboardView
)
from .student_views import student_dashboard
from .home_views import home
from .role_dashboards import (
    club_coordinator_dashboard, svp_dashboard, secretary_dashboard,
    treasurer_dashboard, department_admin_dashboard, club_advisor_dashboard, event_organizer_dashboard,
    student_volunteer_dashboard, faculty_dashboard, admin_dashboard
)
from .role_dashboards import dashboard_redirect
from .auth_views import login_view, logout_view

# Import frontend views
from events.frontend_views import (
    event_list, event_detail, event_create, event_edit, event_delete,
    event_register, event_unregister, event_registrations,
    association_approval_list, approve_association, approve_collaboration
)
from clubs.frontend_views import (
    club_list, club_detail, club_create, club_edit, club_delete, club_join, club_leave
)
from .frontend_views import (
    calendar_view, attendance_manage, profile_view, notifications_list, 
    settings_view, reports_dashboard, attendance_export, attendance_verify
)
from .frontend_views import (
    send_notification, mark_notification_read, mark_notification_unread,
    delete_notification, mark_all_read, clear_all_notifications
)
from .admin_views import (
    assign_club_coordinator, get_students_ajax, event_approval_list, event_approve_reject,
    api_clubs_crud, api_departments_crud, api_users_crud
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("", home, name="home"),
    path("dashboard/", student_dashboard, name="student-dashboard"),
    
    # Custom Admin functions (must come before admin.site.urls)
    path("admin/assign-coordinator/", assign_club_coordinator, name="assign_club_coordinator"),
    path("admin/event-approvals/", event_approval_list, name="event_approval_list"),
    path("admin/event-approve-reject/", event_approve_reject, name="event_approve_reject"),
    path("admin/ajax/students/", get_students_ajax, name="get_students_ajax"),
    
    # Admin API endpoints
    path("api/admin/clubs/", api_clubs_crud, name="api_clubs_crud"),
    path("api/admin/departments/", api_departments_crud, name="api_departments_crud"),
    path("api/admin/users/", api_users_crud, name="api_users_crud"),
    
    # Django Admin (must come after custom admin URLs)
    path("admin/", admin.site.urls),
    path("bulk-upload/", bulk_upload_view, name="bulk-upload"),
    
    # API endpoints
    path("api/", include("users.api_urls")),
    path("api/", include("events.api_urls")),
    path("api/", include("attendance.api_urls")),
    path("api/", include("calendar_app.api_urls")),
    
    # API Dashboard views
    path("api/dashboard/sac/", SACDashboardView.as_view(), name="sac-dashboard"),
    path("api/dashboard/club-coordinator/", ClubCoordinatorDashboardView.as_view(), name="club-coordinator-dashboard"),
    path("api/dashboard/department-admin/", DepartmentAdminDashboardView.as_view(), name="department-admin-dashboard"),
    path("api/dashboard/president/", PresidentDashboardView.as_view(), name="president-dashboard"),
    path("api/dashboard/svp/", SVPDashboardView.as_view(), name="svp-dashboard"),
    path("api/dashboard/secretary/", SecretaryDashboardView.as_view(), name="secretary-dashboard"),
    path("api/dashboard/treasurer/", TreasurerDashboardView.as_view(), name="treasurer-dashboard"),
    path("api/dashboard/club-advisor/", ClubAdvisorDashboardView.as_view(), name="club-advisor-dashboard"),

    # Role-based dashboard template views
    path("dashboard/admin/", admin_dashboard, name="admin-dashboard-template"),
    path("dashboard/club-coordinator/", club_coordinator_dashboard, name="club-coordinator-dashboard-template"),
    path("dashboard/svp/", svp_dashboard, name="svp-dashboard-template"),
    path("dashboard/secretary/", secretary_dashboard, name="secretary-dashboard-template"),
    path("dashboard/treasurer/", treasurer_dashboard, name="treasurer-dashboard-template"),
    path("dashboard/department-admin/", department_admin_dashboard, name="department-admin-dashboard-template"),
    path("dashboard/club-advisor/", club_advisor_dashboard, name="club-advisor-dashboard-template"),
    path("dashboard/event-organizer/", event_organizer_dashboard, name="event-organizer-dashboard-template"),
    path("dashboard/student-volunteer/", student_volunteer_dashboard, name="student-volunteer-dashboard-template"),
    path("dashboard/faculty/", faculty_dashboard, name="faculty-dashboard-template"),
    # Fallback role-based redirect (keep after specific dashboard routes to avoid loops)
    path("dashboard/<str:role>/", dashboard_redirect, name="dashboard"),
    
    # Frontend views
    # Events
    path("events/", event_list, name="event_list"),
    path("events/<int:event_id>/", event_detail, name="event_detail"),
    path("events/create/", event_create, name="event_create"),
    path("events/<int:event_id>/edit/", event_edit, name="event_edit"),
    path("events/<int:event_id>/delete/", event_delete, name="event_delete"),
    path("events/<int:event_id>/register/", event_register, name="event_register"),
    path("events/<int:event_id>/unregister/", event_unregister, name="event_unregister"),
    path("events/<int:event_id>/registrations/", event_registrations, name="event_registrations"),
    path("events/associations/", association_approval_list, name="association_approval_list"),
    path("events/associations/<int:association_id>/approve/", approve_association, name="approve_association"),
    path("events/collaborations/<int:collaboration_id>/approve/", approve_collaboration, name="approve_collaboration"),
    
    # Clubs
    path("clubs/", club_list, name="club_list"),
    path("clubs/<int:club_id>/", club_detail, name="club_detail"),
    path("clubs/create/", club_create, name="club_create"),
    path("clubs/<int:club_id>/edit/", club_edit, name="club_edit"),
    path("clubs/<int:club_id>/delete/", club_delete, name="club_delete"),
    path("clubs/<int:club_id>/join/", club_join, name="club_join"),
    path("clubs/<int:club_id>/leave/", club_leave, name="club_leave"),
    
    # Calendar and Attendance
    path("calendar/", calendar_view, name="calendar_view"),
    path("events/<int:event_id>/attendance/", attendance_manage, name="attendance_manage"),
    path("events/<int:event_id>/attendance/export/", attendance_export, name="attendance_export"),
    path("attendance/verify/", attendance_verify, name="attendance_verify"),
    
    # User pages
    path("profile/", profile_view, name="profile"),
    path("notifications/", notifications_list, name="notifications_list"),
    path("notifications/send/", send_notification, name="send_notification"),
    path("notifications/<int:notification_id>/mark-read/", mark_notification_read, name="mark_notification_read"),
    path("notifications/<int:notification_id>/mark-unread/", mark_notification_unread, name="mark_notification_unread"),
    path("notifications/<int:notification_id>/delete/", delete_notification, name="delete_notification"),
    path("notifications/mark-all-read/", mark_all_read, name="mark_all_read"),
    path("notifications/clear-all/", clear_all_notifications, name="clear_all_notifications"),
    path("settings/", settings_view, name="settings"),
    
    # Reports
    path("reports/", reports_dashboard, name="reports_dashboard"),
    path("bulk-upload/", bulk_upload_view, name="user_bulk_upload"),
]
