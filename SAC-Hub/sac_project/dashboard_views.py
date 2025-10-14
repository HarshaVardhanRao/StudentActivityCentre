
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import User, Club, Department
from events.models import Event, CollaborationRequest
from attendance.models import Attendance
from calendar_app.models import CalendarEntry


class PresidentDashboardView(APIView):

    permission_classes = [IsAuthenticated]
    def get(self, request):
        pending_events = Event.objects.filter(status='PENDING').count()
        approved_events = Event.objects.filter(status='APPROVED').count()
        return Response({
            "pending_events": pending_events,
            "approved_events": approved_events,
        })

class SVPDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        reviewed_events = Event.objects.filter(status='APPROVED').count()
        attendance_reports = Attendance.objects.count()
        return Response({
            "reviewed_events": reviewed_events,
            "attendance_reports": attendance_reports,
        })

class SecretaryDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        events = Event.objects.all()
        pending_reports = events.filter(status='APPROVED').count()
        upcoming_events = events.filter(status='PENDING').count()
        pending_attendance = Attendance.objects.filter(status='PENDING').count() if hasattr(Attendance, 'status') else 0
        return Response({
            "pending_reports": pending_reports,
            "total_events": events.count(),
            "upcoming_events": upcoming_events,
            "pending_attendance": pending_attendance,
        })

class TreasurerDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        events = Event.objects.all()
        pending_reports = events.filter(status='APPROVED').count()
        return Response({
            "pending_reports": pending_reports,
            "total_events": events.count(),
            "pending_requisitions": 0,  # Add when requisition model is available
        })

class ClubAdvisorDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        advised_clubs = Club.objects.filter(advisor=user)
        events = Event.objects.filter(club__in=advised_clubs)
        pending_approvals = events.filter(status='PENDING').count()
        return Response({
            "advised_clubs": advised_clubs.count(),
            "pending_approvals": pending_approvals,
        })
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import User, Club, Department
from events.models import Event, CollaborationRequest
from attendance.models import Attendance
from calendar_app.models import CalendarEntry

class SACDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({
            "pending_events": Event.objects.filter(status='PENDING').count(),
            "pending_collaborations": CollaborationRequest.objects.filter(status='PENDING').count(),
            "total_clubs": Club.objects.count(),
            "total_departments": Department.objects.count(),
        })

class ClubCoordinatorDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        clubs = Club.objects.filter(coordinators=user)
        events = Event.objects.filter(club__in=clubs)
        return Response({
            "my_clubs": clubs.count(),
            "my_events": events.count(),
            "pending_approvals": events.filter(status='PENDING').count(),
        })

class DepartmentAdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        dept = user.department
        events = Event.objects.filter(department=dept)
        attendance = Attendance.objects.filter(event__department=dept)
        return Response({
            "department_events": events.count(),
            "pending_approvals": events.filter(status='PENDING').count(),
            "attendance_records": attendance.count(),
        })
