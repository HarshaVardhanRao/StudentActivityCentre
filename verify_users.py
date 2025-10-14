#!/usr/bin/env python3
"""
Verify created test users
"""
import sys
import os
import django

# Add the project directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'SAC-Hub'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_project.settings')

# Setup Django
django.setup()

from users.models import User, Role

def verify_users():
    """Verify test users were created successfully"""
    print("User Verification Report")
    print("=" * 50)
    
    total_users = User.objects.count()
    print(f"Total users in database: {total_users}")
    
    print("\nUsers by role:")
    
    # Check secretary users specifically
    secretary_users = []
    student_users = []
    
    for user in User.objects.all():
        if Role.SECRETARY in user.roles:
            secretary_users.append(user)
        if Role.STUDENT in user.roles:
            student_users.append(user)
    
    print(f"Secretary users: {len(secretary_users)}")
    for user in secretary_users:
        print(f"  - {user.username} ({user.get_full_name()}): {user.roles}")
    
    print(f"\nStudent users: {len(student_users)}")
    for user in student_users[:5]:  # Show first 5
        print(f"  - {user.username} ({user.get_full_name()}): {user.roles}")
    if len(student_users) > 5:
        print(f"  ... and {len(student_users) - 5} more")
    
    # Check specific test users
    test_usernames = ['ST2024001', 'ST2024002', 'SEC2024001', 'admin', 'sac_coordinator']
    print(f"\nVerifying key test users:")
    for username in test_usernames:
        try:
            user = User.objects.get(username=username)
            print(f"  ✓ {username}: {user.get_full_name()} - {user.roles}")
        except User.DoesNotExist:
            print(f"  ✗ {username}: NOT FOUND")
    
    print(f"\n✅ Verification complete!")

if __name__ == "__main__":
    verify_users()