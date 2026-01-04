import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'SAC-Hub')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_project.settings')
django.setup()

from users.models import User, Department

def verify_admin_dashboard():
    print("Verifying Admin Dashboard...")
    client = Client()

    # 1. Create Admin User
    admin_username = 'verify_admin_001'
    password = 'testpass123'
    try:
        admin = User.objects.get(username=admin_username)
        admin.delete()
    except User.DoesNotExist:
        pass
    
    admin = User.objects.create_user(username=admin_username, password=password, email='admin@example.com')
    admin.roles = ['ADMIN']
    admin.save()
    print(f"Created admin: {admin_username}")

    # 2. Create Test Data
    dept = Department.objects.create(name="Test Dept", description="Test Description")
    print(f"Created department: {dept.name}")

    # 3. Login
    client.force_login(admin)

    # 4. Get Dashboard
    # Using the direct URL name for admin dashboard template
    response = client.get(reverse('admin-dashboard-template'))
    
    if response.status_code != 200:
        print(f"FAILED: Dashboard returned status {response.status_code}")
        # Check if it rendered the error template (admin_dashboard.html) instead of unified
        if b"You do not have permission" in response.content:
             print("FAILED: Permission denied error.")
        return

    content = response.content.decode()
    
    # 5. Verify Content
    if "Manage Users" in content:
        print("SUCCESS: 'Manage Users' section found.")
    else:
        print("FAILED: 'Manage Users' section missing.")

    if "Manage Departments" in content:
        print("SUCCESS: 'Manage Departments' section found.")
    else:
        print("FAILED: 'Manage Departments' section missing.")

    if "Test Dept" in content:
        print("SUCCESS: Test department found in dashboard.")
    else:
        print("FAILED: Test department missing.")

    if admin_username in content:
        print("SUCCESS: Admin user found in user list.")
    else:
        print("FAILED: Admin user missing from user list.")

    # Cleanup
    admin.delete()
    dept.delete()

if __name__ == "__main__":
    verify_admin_dashboard()
