#!/usr/bin/env python
"""
Comprehensive test to verify CLUB_COORDINATOR role management
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/workspaces/StudentActivityCentre/SAC-Hub')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_project.settings')
django.setup()

from users.models import Club, User, Department

def comprehensive_test():
    """Comprehensive test of CLUB_COORDINATOR role management"""
    print("=" * 70)
    print("COMPREHENSIVE TEST: CLUB_COORDINATOR Role Management")
    print("=" * 70)
    
    # Setup
    dept, _ = Department.objects.get_or_create(name="Test Department")
    
    # Test 1: Single coordinator
    print("\n[TEST 1] Single Coordinator Assignment")
    print("-" * 70)
    user1, _ = User.objects.get_or_create(
        username="user1_coordinator",
        defaults={
            'email': 'user1@example.com',
            'first_name': 'User', 'last_name': 'One',
            'roles': ['STUDENT'],
            'department': dept
        }
    )
    print(f"Created user: {user1.username}, roles: {user1.roles}")
    
    club1, _ = Club.objects.get_or_create(
        name="Club 1",
        defaults={'description': 'Test Club 1'}
    )
    club1.coordinators.add(user1)
    user1.refresh_from_db()
    
    assert 'CLUB_COORDINATOR' in user1.roles, "CLUB_COORDINATOR not added!"
    print(f"After adding as coordinator: roles = {user1.roles}")
    print("✓ Test 1 passed: CLUB_COORDINATOR role added")
    
    # Test 2: Multiple clubs
    print("\n[TEST 2] User Coordinating Multiple Clubs")
    print("-" * 70)
    club2, _ = Club.objects.get_or_create(
        name="Club 2",
        defaults={'description': 'Test Club 2'}
    )
    club2.coordinators.add(user1)
    user1.refresh_from_db()
    
    assert 'CLUB_COORDINATOR' in user1.roles, "CLUB_COORDINATOR should still be present!"
    print(f"After adding to 2nd club: roles = {user1.roles}")
    print("✓ Test 2 passed: CLUB_COORDINATOR maintained for multiple clubs")
    
    # Test 3: Removing from one club (but still coordinator of another)
    print("\n[TEST 3] Removing from One Club (Still Coordinator of Another)")
    print("-" * 70)
    club1.coordinators.remove(user1)
    user1.refresh_from_db()
    
    assert 'CLUB_COORDINATOR' in user1.roles, "CLUB_COORDINATOR should remain (still coords club2)!"
    print(f"After removing from club 1: roles = {user1.roles}")
    print("✓ Test 3 passed: CLUB_COORDINATOR role maintained")
    
    # Test 4: Removing from all clubs
    print("\n[TEST 4] Removing from All Clubs")
    print("-" * 70)
    club2.coordinators.remove(user1)
    user1.refresh_from_db()
    
    assert 'CLUB_COORDINATOR' not in user1.roles, "CLUB_COORDINATOR should be removed!"
    print(f"After removing from all clubs: roles = {user1.roles}")
    print("✓ Test 4 passed: CLUB_COORDINATOR role removed")
    
    # Test 5: Multiple coordinators
    print("\n[TEST 5] Multiple Coordinators for One Club")
    print("-" * 70)
    user2, _ = User.objects.get_or_create(
        username="user2_coordinator",
        defaults={
            'email': 'user2@example.com',
            'first_name': 'User', 'last_name': 'Two',
            'roles': ['STUDENT'],
            'department': dept
        }
    )
    user3, _ = User.objects.get_or_create(
        username="user3_coordinator",
        defaults={
            'email': 'user3@example.com',
            'first_name': 'User', 'last_name': 'Three',
            'roles': ['STUDENT'],
            'department': dept
        }
    )
    
    club3, _ = Club.objects.get_or_create(
        name="Club 3",
        defaults={'description': 'Test Club 3'}
    )
    
    club3.coordinators.add(user1, user2, user3)
    user1.refresh_from_db()
    user2.refresh_from_db()
    user3.refresh_from_db()
    
    assert 'CLUB_COORDINATOR' in user1.roles, "User1 should have CLUB_COORDINATOR!"
    assert 'CLUB_COORDINATOR' in user2.roles, "User2 should have CLUB_COORDINATOR!"
    assert 'CLUB_COORDINATOR' in user3.roles, "User3 should have CLUB_COORDINATOR!"
    
    print(f"User 1 roles: {user1.roles}")
    print(f"User 2 roles: {user2.roles}")
    print(f"User 3 roles: {user3.roles}")
    print("✓ Test 5 passed: Multiple coordinators all have CLUB_COORDINATOR role")
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED!")
    print("=" * 70)
    return True

if __name__ == '__main__':
    try:
        success = comprehensive_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
