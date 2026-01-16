
import os
import django
from django.conf import settings
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sac_project.settings")
django.setup()

from events.models import Event, EventStatus, EventRegistration
from attendance.models import Attendance, AttendanceSession, AttendanceStatus
from users.models import Club, Role

User = get_user_model()

class MyEventsVerification(TestCase):
    def setUp(self):
        self.client = Client()
        self.club = Club.objects.create(name="Test Club", description="Test Desc")
        self.student = User.objects.create_user(username="student", email="student@test.com", password="password", roles=[Role.STUDENT])
        
        now = timezone.now()
        
        # 1. Upcoming Registered Event
        self.event_registered = Event.objects.create(
            name="Upcoming Registered Event", 
            date_time=now + timedelta(days=5), 
            status=EventStatus.APPROVED, 
            club=self.club
        )
        EventRegistration.objects.create(event=self.event_registered, student=self.student, status='REGISTERED')
        
        # 2. Past Participated Event (No Registration record, or maybe yes, but Attendance matters)
        self.event_participated = Event.objects.create(
            name="Past Participated Event", 
            date_time=now - timedelta(days=5), 
            status=EventStatus.COMPLETED, 
            club=self.club
        )
        session = AttendanceSession.objects.create(event=self.event_participated)
        Attendance.objects.create(session=session, student=self.student, status=AttendanceStatus.PRESENT)

    def test_my_events_includes_participated(self):
        print("\nTesting My Events List...")
        self.client.force_login(self.student)
        response = self.client.get('/dashboard/')
        
        # Check context
        my_events = response.context['my_events']
        
        # Extract names (handling dict or object)
        event_names = []
        for item in my_events:
            if isinstance(item, dict):
                event_names.append(item['event'].name)
            else:
                event_names.append(item.event.name) # EventRegistration object
        
        print(f"Events found in My Events: {event_names}")
        
        is_registered_present = "Upcoming Registered Event" in event_names
        is_participated_present = "Past Participated Event" in event_names
        
        print(f"Registered Present: {is_registered_present}")
        print(f"Participated Present: {is_participated_present}")
        
        self.assertTrue(is_registered_present, "Upcoming registered event should be visible")
        self.assertTrue(is_participated_present, "Past participated event should be visible")

if __name__ == "__main__":
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'test', 'tests.verify_my_events'])
    except Exception as e:
        print(f"Error: {e}")
