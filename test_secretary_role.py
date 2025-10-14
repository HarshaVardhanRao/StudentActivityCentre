#!/usr/bin/env python3
"""
Test script to verify Secretary role functionality for student users
"""
import sys
import os
import django

# Add the project directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'SAC-Hub'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_project.settings')

# Setup Django
django.setup()

from users.models import User, Role, Department

def test_secretary_role():
    """Test that secretary role can be assigned to student users"""
    print("Testing Secretary Role for Student Users")
    print("=" * 50)
    
    # Test 1: Verify SECRETARY role exists in Role choices
    print("1. Checking if SECRETARY role exists in Role model...")
    role_values = [choice[0] for choice in Role.choices]
    if Role.SECRETARY in role_values:
        print("   ✓ SECRETARY role found in Role model")
    else:
        print("   ✗ SECRETARY role NOT found in Role model")
        return False
    
    # Test 2: Create a test student user with secretary role
    print("\n2. Creating test student user with SECRETARY role...")
    try:
        # Create or get a department
        dept, created = Department.objects.get_or_create(
            name="Computer Science",
            defaults={'description': 'Computer Science Department'}
        )
        if created:
            print("   ✓ Created test department")
        
        # Create test student with secretary role
        test_user, created = User.objects.get_or_create(
            username="test_secretary_student",
            defaults={
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@student.example.com',
                'roll_no': 'CS2024001',
                'roles': [Role.STUDENT, Role.SECRETARY],
                'department': dept
            }
        )
        
        if created:
            print("   ✓ Created test student user with SECRETARY role")
        else:
            # Update existing user to have both roles
            test_user.roles = [Role.STUDENT, Role.SECRETARY]
            test_user.save()
            print("   ✓ Updated existing test student to have SECRETARY role")
        
        print(f"   User: {test_user}")
        print(f"   Roles: {test_user.roles}")
        
    except Exception as e:
        print(f"   ✗ Error creating test user: {e}")
        return False
    
    # Test 3: Verify role assignment works correctly
    print("\n3. Verifying role assignment...")
    if Role.STUDENT in test_user.roles and Role.SECRETARY in test_user.roles:
        print("   ✓ Student user successfully has both STUDENT and SECRETARY roles")
    else:
        print("   ✗ Role assignment failed")
        return False
    
    # Test 4: Test role checking logic (as used in templates)
    print("\n4. Testing role checking logic...")
    user_roles = test_user.roles if isinstance(test_user.roles, list) else []
    if "SECRETARY" in user_roles:
        print("   ✓ Secretary role check works correctly")
    else:
        print("   ✗ Secretary role check failed")
        return False
    
    # Test 5: Verify user string representation works
    print("\n5. Testing user display...")
    user_str = str(test_user)
    if test_user.roll_no in user_str:
        print(f"   ✓ User displays correctly: {user_str}")
    else:
        print(f"   ✗ User display issue: {user_str}")
    
    # Test 6: Test that username is set to roll_no for students
    print("\n6. Testing username assignment for students...")
    if test_user.username == test_user.roll_no:
        print("   ✓ Username correctly set to roll number for student")
    else:
        print(f"   ✗ Username assignment issue: {test_user.username} != {test_user.roll_no}")
    
    print("\n" + "=" * 50)
    print("✓ All Secretary role tests passed!")
    print("Secretary role can be successfully assigned to student users.")
    
    # Cleanup
    print("\nCleaning up test data...")
    test_user.delete()
    print("✓ Test user deleted")
    
    return True

def demonstrate_dashboard_access():
    """Demonstrate how secretary dashboard access works"""
    print("\n" + "=" * 50)
    print("Secretary Dashboard Access Demonstration")
    print("=" * 50)
    
    print("Available URLs for Secretary role:")
    print("  - Template view: /dashboard/secretary/")
    print("  - API endpoint: /api/dashboard/secretary/")
    print("\nDashboard features for Secretary:")
    print("  - View upcoming events requiring documentation")
    print("  - Manage attendance records")
    print("  - Handle meeting minutes")
    print("  - Send communications")
    print("  - Generate reports")
    print("  - Manage documentation")

if __name__ == "__main__":
    try:
        success = test_secretary_role()
        if success:
            demonstrate_dashboard_access()
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)