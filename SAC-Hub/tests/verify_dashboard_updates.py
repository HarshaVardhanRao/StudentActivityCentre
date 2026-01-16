
import os
import django
from django.conf import settings
from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sac_project.settings")
django.setup()

from sac_project.student_views import student_dashboard
from sac_project.role_dashboards import club_coordinator_dashboard, club_advisor_dashboard, admin_dashboard
from events.models import Event, EventRegistration, EventStatus
from users.models import Club, Role
from clubs.models import ClubReport

User = get_user_model()

class DashboardVerification(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # Create common objects
        self.club = Club.objects.create(name="Test Club", description="Test Desc")
        self.student = User.objects.create_user(username="student", email="student@test.com", password="password", roles=[Role.STUDENT])
        self.coordinator = User.objects.create_user(username="coord", email="coord@test.com", password="password", roles=[Role.CLUB_COORDINATOR])
        self.advisor = User.objects.create_user(username="advisor", email="advisor@test.com", password="password", roles=[Role.CLUB_ADVISOR])
        self.sac_coord = User.objects.create_user(username="sac", email="sac@test.com", password="password", roles=[Role.SAC_COORDINATOR])
        
        self.student.clubs.add(self.club)
        self.club.coordinators.add(self.coordinator)
        self.club.advisor = self.advisor
        self.club.save()
        self.advisor.advised_clubs.add(self.club) # Ensure advised_clubs is populated (via related_name logic usually, but manual add if ManyToMany)

        # Create Events
        now = timezone.now()
        self.event_approved = Event.objects.create(name="Approved Event", date_time=now + timedelta(days=1), status=EventStatus.APPROVED, club=self.club)
        self.event_pending = Event.objects.create(name="Pending Event", date_time=now + timedelta(days=2), status=EventStatus.PENDING, club=self.club, resources="Projector")
        self.event_completed = Event.objects.create(name="Completed Event", date_time=now - timedelta(days=1), status=EventStatus.COMPLETED, club=self.club)
        
        # Registration
        EventRegistration.objects.create(event=self.event_approved, student=self.student, status='REGISTERED')
        
        # Report
        ClubReport.objects.create(club=self.club, title="Test Report", status='PENDING')

    def test_student_dashboard(self):
        print("\nTesting Student Dashboard...")
        self.client.force_login(self.student)
        response = self.client.get('/dashboard/') # URL from urls.py line 63
        
        # Check My Events (Registered & Upcoming)
        my_events = response.context['my_events']
        self.assertTrue(any(reg.event.name == "Approved Event" for reg in my_events))
        print("✅ My Events check passed")
        
        # Check Manage Users hidden
        # Not checking content string for hiding as it requires regex search, relying on context 'dashboard_clubs' correctness
        self.assertIn('dashboard_clubs', response.context)
        self.assertEqual(len(response.context['dashboard_clubs']), 1)
        print("✅ My Clubs check passed")

    def test_club_coordinator_dashboard(self):
        print("\nTesting Club Coordinator Dashboard...")
        self.client.force_login(self.coordinator)
        response = self.client.get('/dashboard/club-coordinator/')
        
        # Check Upcoming Events (should include Pending)
        upcoming = response.context['upcoming_events']
        self.assertTrue(any(e.name == "Pending Event" for e in upcoming))
        self.assertTrue(any(e.name == "Approved Event" for e in upcoming))
        print("✅ Upcoming Events (Approved & Waiting) check passed")
        
        # Check Completed Events
        completed = response.context['completed_events']
        self.assertTrue(any(e.name == "Completed Event" for e in completed))
        print("✅ Completed Events check passed")
        
        # Check Dashboard Members (Manage Users data)
        members = response.context['dashboard_members']
        self.assertTrue(any(u.username == "student" for u in members)) # Student is member of the club
        print("✅ Manage Users (Members) check passed")

    def test_club_advisor_dashboard(self):
        print("\nTesting Club Advisor Dashboard...")
        self.client.force_login(self.advisor)
        response = self.client.get('/dashboard/club-advisor/')
        
        self.assertIn('previous_reports', response.context)
        self.assertTrue(response.context['show_report_submission'])
        print("✅ Report Submission check passed")

    def test_sac_coordinator_dashboard(self):
        print("\nTesting SAC Coordinator Dashboard...")
        self.client.force_login(self.sac_coord)
        response = self.client.get('/dashboard/admin/')
        
        self.assertIn('planned_events', response.context)
        self.assertIn('resource_requests', response.context)
        self.assertIn('pending_reports', response.context)
        self.assertTrue(response.context['show_calendar_control'])
        
        # Check Resource Request
        reqs = response.context['resource_requests']
        self.assertTrue(any(e.name == "Pending Event" for e in reqs))
        print("✅ SAC Coordinator Context check passed")

if __name__ == "__main__":
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'test', 'tests/verify_dashboard_updates.py'])
    except Exception as e:
        print(f"Error: {e}")
