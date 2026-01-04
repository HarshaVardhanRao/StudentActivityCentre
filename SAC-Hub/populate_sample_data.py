import os
import django
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command
from users.models import Department, Club, Role

User = get_user_model()

def populate_data():
    print("Clearing database...")
    call_command('flush', '--no-input')
    
    print("Creating sample data...")
    
    # Create Departments
    dept_cse = Department.objects.create(name="Computer Science", description="CSE Department")
    dept_ece = Department.objects.create(name="Electronics", description="ECE Department")
    
    # Create Clubs
    club_coding = Club.objects.create(name="Coding Club", description="For programming enthusiasts")
    club_robotics = Club.objects.create(name="Robotics Club", description="Building the future")
    
    credentials = []
    
    # Create Admin
    admin = User.objects.create_superuser('admin', 'admin@sac.com', 'adminpass')
    admin.roles = [Role.ADMIN]
    admin.save()
    credentials.append("Admin: admin / adminpass")
    
    # Create Faculty Advisors
    advisors = []
    for i in range(1, 3):
        username = f'advisor{i}'
        password = f'advisor{i}pass'
        user = User.objects.create_user(
            username=username,
            email=f'advisor{i}@sac.com',
            password=password,
            first_name=f'Faculty',
            last_name=f'Advisor {i}'
        )
        user.roles = [Role.FACULTY, Role.CLUB_ADVISOR]
        user.department = dept_cse if i == 1 else dept_ece
        user.save()
        advisors.append(user)
        credentials.append(f"Faculty Advisor {i}: {username} / {password}")
        
    # Assign advisors to clubs
    club_coding.advisor = advisors[0]
    club_coding.save()
    club_robotics.advisor = advisors[1]
    club_robotics.save()
    
    # Create Club Coordinators
    coordinators = []
    for i in range(1, 3):
        roll_no = f'COORD{i}00'
        password = f'coord{i}pass'
        user = User.objects.create_user(
            username=roll_no,
            email=f'coord{i}@sac.com',
            password=password,
            first_name=f'Club',
            last_name=f'Coordinator {i}',
            roll_no=roll_no
        )
        user.roles = [Role.STUDENT, Role.CLUB_COORDINATOR]
        user.department = dept_cse if i == 1 else dept_ece
        user.year_of_study = "3rd Year"
        user.save()
        coordinators.append(user)
        credentials.append(f"Club Coordinator {i}: {roll_no} / {password}")
        
    # Assign coordinators to clubs
    club_coding.coordinators.add(coordinators[0])
    club_robotics.coordinators.add(coordinators[1])
    
    # Create Students
    for i in range(1, 11):
        roll_no = f'STUD{i:03d}'
        password = f'stud{i}pass'
        dept = dept_cse if i <= 5 else dept_ece
        user = User.objects.create_user(
            username=roll_no,
            email=f'student{i}@sac.com',
            password=password,
            first_name=f'Student',
            last_name=f'{i}',
            roll_no=roll_no
        )
        user.roles = [Role.STUDENT]
        user.department = dept
        user.year_of_study = random.choice(["1st Year", "2nd Year", "3rd Year", "4th Year"])
        user.section = random.choice(["A", "B", "C"])
        user.save()
        
        # Add students to clubs randomly
        if random.choice([True, False]):
            user.clubs.add(club_coding)
        if random.choice([True, False]):
            user.clubs.add(club_robotics)
            
        credentials.append(f"Student {i}: {roll_no} / {password}")
        
    # Write credentials to file
    with open('sample_credentials.txt', 'w') as f:
        f.write("\n".join(credentials))
        
    print("Sample data created successfully!")
    print("Credentials saved to sample_credentials.txt")

if __name__ == '__main__':
    populate_data()
