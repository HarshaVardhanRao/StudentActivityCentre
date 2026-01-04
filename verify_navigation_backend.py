import os
import sys
import django
from django.test import Client
from django.urls import reverse

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'SAC-Hub')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sac_project.settings')
django.setup()

def verify_navigation():
    print("Verifying Navigation...")
    client = Client()

    # 1. Get About Page
    try:
        url = reverse('about')
        print(f"URL for 'about': {url}")
    except Exception as e:
        print(f"FAILED: Could not reverse 'about': {e}")
        return

    response = client.get(url)
    
    if response.status_code != 200:
        print(f"FAILED: About page returned status {response.status_code}")
        return

    content = response.content.decode()
    
    # 2. Verify Content
    if "About Us" in content:
        print("SUCCESS: 'About Us' found in content.")
    else:
        print("FAILED: 'About Us' missing from content.")

    if "Our Mission" in content:
        print("SUCCESS: 'Our Mission' found in content.")
    else:
        print("FAILED: 'Our Mission' missing from content.")

if __name__ == "__main__":
    verify_navigation()
