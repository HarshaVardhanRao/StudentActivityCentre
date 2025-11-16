#!/usr/bin/env python
"""
Test script to verify that CLUB_COORDINATOR role is added to users when they become club coordinators
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/workspaces/StudentActivityCentre/SAC-Hub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_project.settings')
django.setup()

from users.models import Club, User, Department
from django.db.models.signals import m2m_changed

def test_club_coordinator_role():
    """Test that CLUB_COORDINATOR role is added to coordinators"""
    print("=" * 60)
    print("Testing CLUB_COORDINATOR Role Assignment")
    print("=" * 60)
    
    # Check if signals are connected
    print("\nChecking signal receivers...")
    receivers = m2m_changed.receivers
    print(f"Number of m2m_changed receivers: {len(receivers)}")
    for receiver in receivers:
        print(f"  - {receiver}")
    
    # Create a test department if needed
    dept, _ = Department.objects.get_or_create(name="Test Department")
    
    # Create a test user
    test_user, created = User.objects.get_or_create(
        username="testcoord123",
        defaults={
            'email': 'testcoord@example.com',
            'first_name': 'Test',
            'last_name': 'Coordinator',
            'roles': ['STUDENT'],  # Start without CLUB_COORDINATOR role
            'department': dept
        }
    )
    
    print(f"\n1. Created test user: {test_user.username}")
    print(f"   Initial roles: {test_user.roles}")
    
    # Create a test club
    club, created = Club.objects.get_or_create(
        name="Test Club for Role Assignment 2",
        defaults={'description': 'A test club to verify role assignment'}
    )
    
    print(f"\n2. Created test club: {club.name}")
    
    # Add the user as a coordinator
    print(f"\n3. Adding {test_user.username} as a coordinator to {club.name}...")
    club.coordinators.add(test_user)
    
    # Refresh the user from database
    test_user.refresh_from_db()
    
    print(f"   Roles after adding as coordinator: {test_user.roles}")
    
    # Check if CLUB_COORDINATOR is in roles
    if 'CLUB_COORDINATOR' in test_user.roles:
        print("\n✓ SUCCESS: CLUB_COORDINATOR role was added!")
        return True
    else:
        print("\n✗ FAILED: CLUB_COORDINATOR role was NOT added!")
        print(f"   Expected: 'CLUB_COORDINATOR' in {test_user.roles}")
        return False

if __name__ == '__main__':
    success = test_club_coordinator_role()
    sys.exit(0 if success else 1)

