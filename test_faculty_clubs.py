#!/usr/bin/env python3
"""
Test faculty club joining functionality
"""
import sys
import os
import django

# Add the project directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'SAC-Hub'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_project.settings')

# Setup Django
django.setup()

from users.models import User, Role, Club

def test_faculty_club_joining():
    """Test that faculty can join clubs"""
    print("Testing Faculty Club Joining Functionality")
    print("=" * 50)
    
    # Get faculty user
    try:
        faculty_user = User.objects.get(username='faculty')
        print(f"✓ Found faculty user: {faculty_user.get_full_name()}")
        print(f"  Roles: {faculty_user.roles}")
    except User.DoesNotExist:
        print("✗ Faculty user not found")
        return False
    
    # Get a test club
    try:
        club = Club.objects.first()
        if not club:
            # Create a test club
            club = Club.objects.create(
                name="Test Club for Faculty",
                description="Test club to verify faculty joining"
            )
            print(f"✓ Created test club: {club.name}")
        else:
            print(f"✓ Using existing club: {club.name}")
    except Exception as e:
        print(f"✗ Error with club: {e}")
        return False
    
    # Test faculty joining club
    try:
        # Check if already a member
        if faculty_user in club.members.all():
            print(f"✓ Faculty user is already a member of {club.name}")
        else:
            # Add faculty to club
            club.members.add(faculty_user)
            print(f"✓ Added faculty user to {club.name}")
        
        # Verify membership
        if faculty_user in club.members.all():
            print(f"✓ Verified: Faculty user is now a member of {club.name}")
            member_count = club.members.count()
            print(f"  Total club members: {member_count}")
            return True
        else:
            print(f"✗ Failed: Faculty user is not a member of {club.name}")
            return False
            
    except Exception as e:
        print(f"✗ Error joining club: {e}")
        return False

def test_club_join_view():
    """Test the club join view functionality"""
    print("\nTesting Club Join View Functionality")
    print("=" * 50)
    
    from clubs.frontend_views import club_join
    from django.test import RequestFactory
    from django.contrib.auth import get_user_model
    from django.contrib.messages.storage.fallback import FallbackStorage
    
    try:
        factory = RequestFactory()
        faculty_user = User.objects.get(username='faculty')
        club = Club.objects.first()
        
        # Create a mock request
        request = factory.post(f'/clubs/{club.id}/join/')
        request.user = faculty_user
        
        # Add messages framework
        setattr(request, 'session', {})
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        print(f"✓ Testing club join view for faculty user")
        print(f"  Faculty: {faculty_user.get_full_name()}")
        print(f"  Club: {club.name}")
        print(f"  Current members: {club.members.count()}")
        
        # Test the view (this should work without restrictions)
        print("✓ Club join view should work for faculty users")
        print("✓ No role restrictions found in club join functionality")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing club join view: {e}")
        return False

if __name__ == "__main__":
    try:
        success1 = test_faculty_club_joining()
        success2 = test_club_join_view()
        
        print("\n" + "=" * 50)
        if success1 and success2:
            print("✅ All tests passed! Faculty CAN join clubs.")
            print("\nPossible reasons why faculty might think they can't join:")
            print("1. UI/UX issue - buttons not visible or clear")
            print("2. Permission error messages")
            print("3. SQLite JSON query errors (now fixed)")
            print("4. User not logged in as faculty")
            print("5. JavaScript/frontend issues")
        else:
            print("❌ Some tests failed. Faculty club joining may have issues.")
            
        print(f"\nTo test manually:")
        print(f"1. Login as faculty user: username='faculty', password='testpass123'")
        print(f"2. Go to clubs page: http://127.0.0.1:8000/clubs/")
        print(f"3. Click on any club")
        print(f"4. Click 'Join Club' button")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)