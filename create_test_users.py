#!/usr/bin/env python3
"""
Script to create test users for all roles in the Student Activity Centre
"""
import sys
import os
import django
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'SAC-Hub'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_project.settings')

# Setup Django
django.setup()

from users.models import User, Role, Department, Club
from django.contrib.auth.hashers import make_password

def create_test_users():
    """Create test users for all roles"""
    print("Creating test users for Student Activity Centre")
    print("=" * 60)
    
    # Create or get departments
    cs_dept, _ = Department.objects.get_or_create(
        name="Computer Science",
        defaults={'description': 'Computer Science Department'}
    )
    
    ece_dept, _ = Department.objects.get_or_create(
        name="Electronics & Communication",
        defaults={'description': 'Electronics & Communication Engineering Department'}
    )
    
    me_dept, _ = Department.objects.get_or_create(
        name="Mechanical Engineering",
        defaults={'description': 'Mechanical Engineering Department'}
    )
    
    # Create or get clubs
    tech_club, _ = Club.objects.get_or_create(
        name="Technology Club",
        defaults={'description': 'Technology and Innovation Club'}
    )
    
    cultural_club, _ = Club.objects.get_or_create(
        name="Cultural Club",
        defaults={'description': 'Cultural Activities Club'}
    )
    
    sports_club, _ = Club.objects.get_or_create(
        name="Sports Club",
        defaults={'description': 'Sports and Athletics Club'}
    )
    
    # User data with credentials
    users_data = []
    
    # Password for all test users
    default_password = "testpass123"
    
    # Create test users for each role
    test_users = [
        # 2 Students
        {
            'username': 'ST2024001',
            'first_name': 'Alice',
            'last_name': 'Johnson',
            'email': 'alice.johnson@student.edu',
            'roll_no': 'ST2024001',
            'roles': [Role.STUDENT],
            'department': cs_dept,
            'is_student': True
        },
        {
            'username': 'ST2024002',
            'first_name': 'Bob',
            'last_name': 'Smith',
            'email': 'bob.smith@student.edu',
            'roll_no': 'ST2024002',
            'roles': [Role.STUDENT],
            'department': ece_dept,
            'is_student': True
        },
        
        # SAC Coordinator
        {
            'username': 'sac_coordinator',
            'first_name': 'Sarah',
            'last_name': 'Wilson',
            'email': 'sarah.wilson@sac.edu',
            'roll_no': None,
            'roles': [Role.SAC_COORDINATOR, Role.STUDENT],
            'department': cs_dept,
            'is_student': False
        },
        
        # Co-Coordinator
        {
            'username': 'co_coordinator',
            'first_name': 'Mike',
            'last_name': 'Davis',
            'email': 'mike.davis@sac.edu',
            'roll_no': None,
            'roles': [Role.CO_COORDINATOR, Role.STUDENT],
            'department': ece_dept,
            'is_student': False
        },
        
        # Department Admin
        {
            'username': 'dept_admin',
            'first_name': 'Linda',
            'last_name': 'Brown',
            'email': 'linda.brown@dept.edu',
            'roll_no': None,
            'roles': [Role.DEPARTMENT_ADMIN],
            'department': cs_dept,
            'is_student': False
        },
        
        # President
        {
            'username': 'president',
            'first_name': 'John',
            'last_name': 'Anderson',
            'email': 'john.anderson@president.edu',
            'roll_no': 'PR2024001',
            'roles': [Role.PRESIDENT, Role.STUDENT],
            'department': cs_dept,
            'is_student': True
        },
        
        # Senior VP
        {
            'username': 'svp',
            'first_name': 'Emma',
            'last_name': 'Taylor',
            'email': 'emma.taylor@svp.edu',
            'roll_no': 'VP2024001',
            'roles': [Role.SVP, Role.STUDENT],
            'department': ece_dept,
            'is_student': True
        },
        
        # Secretary
        {
            'username': 'secretary',
            'first_name': 'David',
            'last_name': 'Miller',
            'email': 'david.miller@secretary.edu',
            'roll_no': 'SEC2024001',
            'roles': [Role.SECRETARY, Role.STUDENT],
            'department': me_dept,
            'is_student': True
        },
        
        # Treasurer
        {
            'username': 'treasurer',
            'first_name': 'Lisa',
            'last_name': 'Garcia',
            'email': 'lisa.garcia@treasurer.edu',
            'roll_no': 'TR2024001',
            'roles': [Role.TREASURER, Role.STUDENT],
            'department': cs_dept,
            'is_student': True
        },
        
        # Department VP
        {
            'username': 'dept_vp',
            'first_name': 'James',
            'last_name': 'Rodriguez',
            'email': 'james.rodriguez@deptvp.edu',
            'roll_no': 'DVP2024001',
            'roles': [Role.DEPARTMENT_VP, Role.STUDENT],
            'department': ece_dept,
            'is_student': True
        },
        
        # Club Coordinator
        {
            'username': 'club_coordinator',
            'first_name': 'Maria',
            'last_name': 'Lopez',
            'email': 'maria.lopez@club.edu',
            'roll_no': 'CC2024001',
            'roles': [Role.CLUB_COORDINATOR, Role.STUDENT],
            'department': cs_dept,
            'is_student': True
        },
        
        # Club Advisor
        {
            'username': 'club_advisor',
            'first_name': 'Dr. Robert',
            'last_name': 'Johnson',
            'email': 'robert.johnson@faculty.edu',
            'roll_no': None,
            'roles': [Role.CLUB_ADVISOR, Role.FACULTY],
            'department': cs_dept,
            'is_student': False
        },
        
        # Event Organizer
        {
            'username': 'event_organizer',
            'first_name': 'Anna',
            'last_name': 'Williams',
            'email': 'anna.williams@events.edu',
            'roll_no': 'EO2024001',
            'roles': [Role.EVENT_ORGANIZER, Role.STUDENT],
            'department': me_dept,
            'is_student': True
        },
        
        # Student Volunteer
        {
            'username': 'student_volunteer',
            'first_name': 'Chris',
            'last_name': 'Martinez',
            'email': 'chris.martinez@volunteer.edu',
            'roll_no': 'SV2024001',
            'roles': [Role.STUDENT_VOLUNTEER, Role.STUDENT],
            'department': ece_dept,
            'is_student': True
        },
        
        # Faculty
        {
            'username': 'faculty',
            'first_name': 'Dr. Patricia',
            'last_name': 'Thompson',
            'email': 'patricia.thompson@faculty.edu',
            'roll_no': None,
            'roles': [Role.FACULTY],
            'department': me_dept,
            'is_student': False
        },
        
        # Admin
        {
            'username': 'admin',
            'first_name': 'Administrator',
            'last_name': 'User',
            'email': 'admin@sac.edu',
            'roll_no': None,
            'roles': [Role.ADMIN],
            'department': None,
            'is_student': False
        }
    ]
    
    created_users = []
    
    for user_data in test_users:
        try:
            # Check if user already exists
            existing_user = User.objects.filter(username=user_data['username']).first()
            if existing_user:
                print(f"User {user_data['username']} already exists, updating...")
                user = existing_user
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.email = user_data['email']
                user.roll_no = user_data['roll_no']
                user.roles = user_data['roles']
                user.department = user_data['department']
            else:
                # Create new user
                user = User(
                    username=user_data['username'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email'],
                    roll_no=user_data['roll_no'],
                    roles=user_data['roles'],
                    department=user_data['department']
                )
                print(f"Creating user: {user_data['username']}")
            
            # Set password
            user.set_password(default_password)
            user.save()
            
            # Add to clubs for specific roles
            if Role.CLUB_COORDINATOR in user_data['roles']:
                tech_club.coordinators.add(user)
            
            if Role.CLUB_ADVISOR in user_data['roles']:
                tech_club.advisor = user
                tech_club.save()
            
            created_users.append({
                'username': user.username,
                'password': default_password,
                'email': user.email,
                'full_name': user.get_full_name(),
                'roles': user.roles,
                'roll_no': user.roll_no,
                'department': user.department.name if user.department else 'None'
            })
            
        except Exception as e:
            print(f"Error creating user {user_data['username']}: {e}")
    
    return created_users

def save_credentials_to_file(users_data):
    """Save user credentials to a file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"user_credentials_{timestamp}.txt"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("STUDENT ACTIVITY CENTRE - TEST USER CREDENTIALS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Default Password for all users: testpass123\n")
        f.write("=" * 60 + "\n\n")
        
        # Group users by role
        role_groups = {}
        for user in users_data:
            primary_role = user['roles'][0] if user['roles'] else 'NO_ROLE'
            if primary_role not in role_groups:
                role_groups[primary_role] = []
            role_groups[primary_role].append(user)
        
        for role, users in role_groups.items():
            f.write(f"{role.replace('_', ' ').title()}\n")
            f.write("-" * 40 + "\n")
            for user in users:
                f.write(f"Username: {user['username']}\n")
                f.write(f"Password: {user['password']}\n")
                f.write(f"Email: {user['email']}\n")
                f.write(f"Full Name: {user['full_name']}\n")
                f.write(f"Roles: {', '.join(user['roles'])}\n")
                if user['roll_no']:
                    f.write(f"Roll No: {user['roll_no']}\n")
                f.write(f"Department: {user['department']}\n")
                f.write("\n")
            f.write("\n")
        
        # Add quick reference section
        f.write("QUICK LOGIN REFERENCE\n")
        f.write("=" * 60 + "\n")
        for user in users_data:
            f.write(f"{user['username']} | testpass123 | {user['roles'][0]}\n")
        
        f.write("\n\nLOGIN URLS:\n")
        f.write("- Main Login: http://localhost:8000/login/\n")
        f.write("- Admin Panel: http://localhost:8000/admin/\n")
        f.write("- Student Dashboard: http://localhost:8000/dashboard/\n")
    
    return filepath

if __name__ == "__main__":
    try:
        print("Starting user creation process...")
        users = create_test_users()
        filepath = save_credentials_to_file(users)
        
        print(f"\n✅ Successfully created {len(users)} test users!")
        print(f"📄 Credentials saved to: {filepath}")
        print("\nDefault password for all users: testpass123")
        print("\nTest users created for roles:")
        
        # Count users by role
        role_counts = {}
        for user in users:
            for role in user['roles']:
                role_counts[role] = role_counts.get(role, 0) + 1
        
        for role, count in sorted(role_counts.items()):
            print(f"  - {role.replace('_', ' ').title()}: {count} user(s)")
        
        print(f"\nTotal users created: {len(users)}")
        print(f"Students: {len([u for u in users if 'STUDENT' in u['roles']])}")
        print(f"Faculty: {len([u for u in users if 'FACULTY' in u['roles']])}")
        print(f"Admin: {len([u for u in users if 'ADMIN' in u['roles']])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)