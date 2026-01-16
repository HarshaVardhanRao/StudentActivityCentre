
import os
import django
from django.conf import settings
from django.test import RequestFactory, Client, TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sac_project.settings")
django.setup()

from events.models import Event, EventStatus
from users.models import Club, Role

User = get_user_model()

class EventListVerification(TestCase):
    def setUp(self):
        self.client = Client()
        self.club = Club.objects.create(name="Test Club", description="Test Desc")
        self.student = User.objects.create_user(username="student", email="student@test.com", password="password", roles=[Role.STUDENT])
        
        now = timezone.now()
        
        # Create Upcoming Event
        self.upcoming_event = Event.objects.create(
            name="Upcoming Public Event", 
            date_time=now + timedelta(days=5), 
            status=EventStatus.APPROVED, 
            club=self.club
        )
        
        # Create Past Event
        self.past_event = Event.objects.create(
            name="Past Public Event", 
            date_time=now - timedelta(days=5), 
            status=EventStatus.APPROVED, 
            club=self.club
        )

    def test_event_list_shows_only_upcoming(self):
        print("\nTesting Event List Filtering...")
        self.client.force_login(self.student)
        response = self.client.get('/events/')
        
        # Check context
        events = response.context['events']
        event_names = [e.name for e in events]
        
        print(f"Events found: {event_names}")
        
        # Assertions
        is_upcoming_present = "Upcoming Public Event" in event_names
        is_past_present = "Past Public Event" in event_names
        
        print(f"Upcoming Present: {is_upcoming_present}")
        print(f"Past Present: {is_past_present}")
        
        self.assertTrue(is_upcoming_present, "Upcoming event should be visible")
        self.assertFalse(is_past_present, "Past event should NOT be visible")

if __name__ == "__main__":
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'test', 'tests.verify_event_list'])
    except Exception as e:
        print(f"Error: {e}")
