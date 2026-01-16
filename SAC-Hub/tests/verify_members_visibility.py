
import os
import django
from django.test import Client, TestCase
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sac_project.settings")
django.setup()

from users.models import Club, Role

User = get_user_model()

class MemberVisibilityTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.club = Club.objects.create(name="Test Club", description="Test Desc")
        
        # Student User (Only Student)
        self.student = User.objects.create_user(username="student_only", email="student@test.com", password="password", roles=[Role.STUDENT])
        self.student.clubs.add(self.club)
        
        # Club Coordinator User
        self.coordinator = User.objects.create_user(username="coordinator", email="coord@test.com", password="password", roles=[Role.CLUB_COORDINATOR])
        self.coordinator.coordinated_clubs.add(self.club)
        
        print(f"DEBUG: Student ID={self.student.id}, Coordinator ID={self.coordinator.id}") # Coordinator logic uses coordinated_clubs

    def test_student_visibility(self):
        print("\nTesting Student Member Visibility...")
        # Check roles before login (refresh from DB first)
        self.student.refresh_from_db()
        print(f"User Roles (DB): {self.student.roles}")
        
        # Check if student is in coordinators
        is_coord = self.club.coordinators.filter(id=self.student.id).exists()
        print(f"Is Student in Club.coordinators? {is_coord}")

        self.client.force_login(self.student)
        response = self.client.get('/dashboard/')
        
        # Debugging Context
        print(f"User Roles: {self.student.roles}")
        if 'users' in response.context:
            print(f"Context 'users': {response.context['users']}")
        else:
            print("Context 'users' NOT FOUTD")
            
        content = response.content.decode('utf-8')
        
        # Find where it occurs
        if "Manage Users" in content:
            idx = content.find("Manage Users")
            print(f"Found 'Manage Users' at index {idx}")
            print(f"Surrounding text: {content[max(0, idx-50):idx+50]}")
            print("FAILURE: 'Manage Users' found in Student Dashboard")
        else:
            print("SUCCESS: 'Manage Users' NOT found in Student Dashboard")
            
        self.assertNotIn("Manage Users", content, "Student should not see Manage Users section or link")

    def test_coordinator_visibility(self):
        print("\nTesting Coordinator Member Visibility...")
        self.client.force_login(self.coordinator)
        # Note: Coordinators might be redirected or use the same URL. 
        # dashboard_redirect sends 'club-coordinator' to 'club-coordinator-dashboard-template' -> 'club_coordinator_dashboard' view.
        # But the URL for that view is likely /dashboard/club-coordinator/ (based on dashboard_redirect logic).
        # Let's check urls.py implicitly? No, checking role_dashboards logic:
        # dashboard_redirect uses view names. 
        # Let's try to fetch the specific dashboard URL: /dashboard/club-coordinator/
        
        response = self.client.get('/dashboard/club-coordinator/')
        
        content = response.content.decode('utf-8')
        
        if "Manage Users" in content:
            print("SUCCESS: 'Manage Users' found in Coordinator Dashboard")
        else:
            print("FAILURE: 'Manage Users' NOT found in Coordinator Dashboard")
            
        self.assertIn("Manage Users", content, "Coordinator should see Manage Users section")
        
if __name__ == "__main__":
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'test', 'tests.verify_members_visibility'])
    except Exception as e:
        print(f"Error: {e}")
