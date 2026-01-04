import os
import sys
import django

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'SAC-Hub')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_project.settings')
django.setup()

from users.models import User

def list_users():
    print("Listing users...")
    users = User.objects.all()
    print(f"Total users: {users.count()}")
    for user in users:
        print(f"- {user.username} ({user.email})")

if __name__ == "__main__":
    list_users()
