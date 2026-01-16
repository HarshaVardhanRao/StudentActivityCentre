
import os
import django
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sac_project.settings")
django.setup()

from events.models import Event, EventStatus
from users.models import Club, Role
from attendance.models import Attendance, AttendanceSession, AttendanceStatus

User = get_user_model()

class DashboardStatsVerification(TestCase):
    def setUp(self):
        self.client = Client()
        self.club = Club.objects.create(name="Test Club", description="Test Desc")
        
        # Student User
        self.student = User.objects.create_user(username="student", email="student@test.com", password="password", roles=[Role.STUDENT])
        self.student.clubs.add(self.club)
        
        # SAC Coordinator User
        self.sac = User.objects.create_user(username="sac", email="sac@test.com", password="password", roles=[Role.SAC_COORDINATOR])
        
        # Data for Student Stats
        # 1. Participated Event
        self.event_p = Event.objects.create(name="Participated", date_time=timezone.now() - timedelta(days=1), status=EventStatus.COMPLETED, club=self.club)
        session = AttendanceSession.objects.create(event=self.event_p)
        Attendance.objects.create(session=session, student=self.student, status=AttendanceStatus.PRESENT)
        
        # Data for SAC Stats
        # 1. Pending Event
        Event.objects.create(name="Pending", date_time=timezone.now() + timedelta(days=1), status=EventStatus.PENDING, club=self.club)

    def test_student_stats(self):
        print("\nTesting Student Dashboard Stats...")
        self.client.force_login(self.student)
        response = self.client.get('/dashboard/')
        
        stats = response.context['stats']
        print(f"Student Stats: {stats}")
        
        self.assertEqual(stats['total_clubs'], 1, "Should have 1 club")
        self.assertEqual(stats['total_users'], 1, "Should have 1 participated event")
        self.assertFalse(stats['is_sac_admin'], "Student should NOT be SAC admin")

    def test_sac_stats(self):
        print("\nTesting SAC Dashboard Stats...")
        self.client.force_login(self.sac)
        response = self.client.get('/dashboard/admin/')
        
        # SAC Dashboard might be using a different view (admin_dashboard) which might need updating if it shares the template
        # Let's check the view logic for admin_dashboard in role_dashboards.py
        # It usually passes stats directly.
        # If the template relies on stats.is_sac_admin, we need to ensure admin_dashboard provides it.
        
        stats = response.context['stats']
        print(f"SAC Stats: {stats}")
        
        self.assertGreaterEqual(stats['total_clubs'], 1)
        self.assertGreaterEqual(stats['pending_events'], 1)
        self.assertTrue(stats['is_sac_admin'], "SAC Admin flag should be True")
        
if __name__ == "__main__":
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'test', 'tests.verify_dashboard_stats'])
    except Exception as e:
        print(f"Error: {e}")
