import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'SAC-Hub')))
print("DEBUG: sys.path:", sys.path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_project.settings')
django.setup()

from users.models import User
from events.models import Event

def verify_backend_creation():
    print("Verifying backend event creation...")
    
    # Get user
    user = User.objects.get(username='CC2024001')
    print(f"User: {user.username}")
    
    # Client
    client = Client()
    client.force_login(user)
    
    # Data
    data = {
        'name': 'Backend Test Event',
        'event_type': 'Test',
        'description': 'Created via backend script',
        'date_time': '2026-02-01T10:00',
        'venue': 'Test Venue',
        'club': user.coordinated_clubs.first().id if user.coordinated_clubs.exists() else '',
        'resources': 'None'
    }
    
    # GET request
    print("Testing GET request...")
    response = client.get(reverse('event_create'))
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        print("GET Success")
        # Check if form is in context
        if 'form' in response.context:
            print(f"Form in context: {response.context['form']}")
        else:
            print("Form NOT in context!")
            
        if 'event' in response.context:
            print(f"Event in context: {response.context['event']}")
        else:
            print("Event NOT in context!")
    else:
        print("GET Failed")
        print(response.content.decode())
        
    return

    # Post
    # response = client.post(reverse('event_create'), data)

if __name__ == "__main__":
    verify_backend_creation()
