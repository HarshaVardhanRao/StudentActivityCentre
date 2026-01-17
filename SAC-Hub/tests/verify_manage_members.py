import os
import sys
import django
from django.conf import settings

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_project.settings')
django.setup()

from django.test import RequestFactory
from django.template.loader import render_to_string
from users.models import User, Club, Department
from clubs.frontend_views import manage_club_members
from django.contrib.auth.models import AnonymousUser

def verify_manage_members():
    # Create test data
    try:
        dept, _ = Department.objects.get_or_create(name="Test Dept")
        
        # Create coordinator/admin user to view the page
        coordinator, _ = User.objects.get_or_create(
            username="test_coord",
            email="coord@example.com",
            department=dept
        )
        coordinator.roles = ['CLUB_COORDINATOR']
        coordinator.year_of_study = 3
        coordinator.save()

        # Create a member
        member, _ = User.objects.get_or_create(
            username="test_member",
            email="member@example.com",
            department=dept
        )
        member.roles = ['STUDENT']
        member.year_of_study = 2
        member.save()

        # Create club
        club, _ = Club.objects.get_or_create(name="Test Club")
        club.coordinators.add(coordinator)
        club.members.add(member)
        club.save()

        print(f"Setup: Club '{club.name}' has members: {[u.username for u in club.members.all()]}")

        # Factory
        factory = RequestFactory()
        
        # Test 1: Basic Load
        request = factory.get(f'/clubs/{club.id}/manage-members/')
        request.user = coordinator
        
        # We can't easily run the view function directly because it relies on messages middleware etc. which Mocking is annoying.
        # easier to just render the template with the context that the view WOULD pass.
        # But to be sure, let's try to mimic the view's context generation logic or just use the template.
        
        # Let's inspect the template rendering directly with context
        from django.core.paginator import Paginator
        
        members_qs = club.members.all()
        paginator = Paginator(members_qs, 15)
        members_page = paginator.get_page(1)
        
        context = {
            'club': club,
            'members': members_page, # This is the key
            'total_members': members_qs.count(),
            'role_filter': '',
            'dept_filter': '',
            'year_filter': '',
            'sort_by': 'name',
            'departments': Department.objects.all(),
            'all_years': [1, 2, 3, 4],
            'is_coordinator': True,
            'is_admin': False,
            'is_advisor': False,
            'request': request # needed for sidebar potentially
        }
        
        # DEBUG: Print file content
        print(f"DEBUG: TEMPLATES setting: {settings.TEMPLATES}", flush=True)
        params_path = os.path.join(settings.BASE_DIR, 'templates/clubs/manage_members_v2.html')
        with open(params_path, 'r') as f:
            print(f"DEBUG: Content of {params_path} around line 60:", flush=True)
            lines = f.readlines()
            for i, line in enumerate(lines):
                if 55 <= i <= 65:
                   print(f"{i+1}: {line}", end='', flush=True)
        


        rendered = render_to_string('clubs/manage_members_v2.html', context)
        
        if "test_member" in rendered:
            print("SUCCESS: 'test_member' found in rendered output.")
        else:
            print("FAILURE: 'test_member' NOT found in rendered output.")
            # Print the table body part to debug
            import re
            match = re.search(r'<tbody.*?</tbody>', rendered, re.DOTALL)
            if match:
                print("DEBUG: Rendered Tbody:")
                print(match.group(0))
            else:
                # print("DEBUG: Tbody not found in rendered output.")
                pass

        if "No members found" in rendered:
             pass
             
        final_status = "FAILURE"
        if "test_member" in rendered:
             final_status = "SUCCESS"
        
        print(f"\nFINAL RESULT: {final_status} - 'test_member' presence check.")
        if "Members Table" in rendered:
             print("Content Block Check: 'Members Table' marker found (Rendering probably OK).")
        else:
             print("Content Block Check: 'Members Table' marker MISSING (Rendering stopped early?).")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_manage_members()
