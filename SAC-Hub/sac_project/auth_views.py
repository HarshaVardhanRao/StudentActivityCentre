from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from users.models import User, Role

import logging
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == "POST":
        # Log incoming POST data (excluding password for security)
        logger.debug(f"Login attempt: username={request.POST.get('username')}")

        username = request.POST.get("username")
        password = request.POST.get("password")

        # Validate fields before authentication
        if not username or not password:
            logger.warning("Login failed: Missing username or password")
            return render(
                request,
                "login.html",
                {"form": {}, "error": "Username and Password are required."}
            )

        try:
            user = authenticate(request, username=username, password=password)
        except Exception as e:
            logger.exception("Error during authentication:")
            return render(
                request,
                "login.html",
                {"form": {}, "error": f"Internal error: {str(e)}"}
            )

        if user is not None:
            logger.info(f"User '{username}' authenticated successfully.")
            login(request, user)
            # Redirect users to role-appropriate dashboards
            roles = getattr(user, 'roles', []) or []

            role_map = {
                'ADMIN': 'admin-dashboard-template',
                'SAC_COORDINATOR': 'admin-dashboard-template',
                'CLUB_COORDINATOR': 'club-coordinator-dashboard-template',
                'SVP': 'svp-dashboard-template',
                'SECRETARY': 'secretary-dashboard-template',
                'TREASURER': 'treasurer-dashboard-template',
                'DEPARTMENT_ADMIN': 'department-admin-dashboard-template',
                'CLUB_ADVISOR': 'club-advisor-dashboard-template',
                'EVENT_ORGANIZER': 'event-organizer-dashboard-template',
                'STUDENT_VOLUNTEER': 'student-volunteer-dashboard-template',
                'FACULTY': 'faculty-dashboard-template',
            }

            # Prefer admin-like roles first
            for r in ['ADMIN', 'SAC_COORDINATOR']:
                if r in roles:
                    return redirect(role_map[r])

            # Then check other roles and redirect to their dashboards
            for r_key, view_name in role_map.items():
                if r_key in roles:
                    return redirect(view_name)

            # Default fallback
            return redirect("student-dashboard")
        else:
            logger.warning(f"Invalid login attempt for username '{username}'")
            return render(
                request,
                "login.html",
                {"form": {}, "error": "Invalid username or password."}
            )

    # GET request
    logger.debug("Rendering login page.")
    return render(request, "login.html", {"form": {}})


def logout_view(request):
    logout(request)
    return redirect("login")
