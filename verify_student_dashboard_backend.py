import os
import sys
import django
from django.test import Client
from django.urls import reverse
from django.utils import timezone

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'SAC-Hub')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_project.settings')
django.setup()

from users.models import User, Notification
from events.models import Event, EventRegistration, EventStatus

def verify_student_dashboard():
    print("Verifying Student Dashboard...")
    client = Client()

    # 1. Create Test Student
    student_username = 'verify_student_001'
    password = 'testpass123'
    try:
        student = User.objects.get(username=student_username)
        student.delete()
    except User.DoesNotExist:
        pass
    
    student = User.objects.create_user(username=student_username, password=password, email='student@example.com')
    print(f"Created student: {student_username}")

    # 2. Create Test Event
    event = Event.objects.create(
        name="Dashboard Test Event",
        event_type="Workshop",
        description="Test Description",
        date_time=timezone.now() + timezone.timedelta(days=1),
        venue="Test Venue",
        status=EventStatus.APPROVED
    )
    print(f"Created event: {event.name}")

    # 3. Register Student for Event
    EventRegistration.objects.create(event=event, student=student)
    print("Registered student for event")

    # 4. Create Notification
    Notification.objects.create(user=student, message="Test Notification")
    print("Created notification for student")

    # 5. Login
    client.force_login(student)

    # 6. Get Dashboard
    response = client.get(reverse('student-dashboard'))
    
    if response.status_code != 200:
        print(f"FAILED: Dashboard returned status {response.status_code}")
        return

    content = response.content.decode()
    
    # 7. Verify Content
    if "My Events" in content:
        print("SUCCESS: 'My Events' section found.")
    else:
        print("FAILED: 'My Events' section missing.")

    if "Dashboard Test Event" in content:
        print("SUCCESS: Test event found in dashboard.")
    else:
        print("FAILED: Test event missing.")

    if "Notifications" in content:
        print("SUCCESS: 'Notifications' section found.")
    else:
        print("FAILED: 'Notifications' section missing.")

    if "Test Notification" in content:
        print("SUCCESS: Test notification found in dashboard.")
    else:
        print("FAILED: Test notification missing.")

    # Cleanup
    student.delete()
    event.delete()

if __name__ == "__main__":
    verify_student_dashboard()
