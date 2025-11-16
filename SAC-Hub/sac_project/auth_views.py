from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from users.models import User, Role

import logging
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.db.models import Q

logger = logging.getLogger(__name__)
User = get_user_model()

def login_view(request):
    if request.method == "POST":

        logger.debug(f"Login attempt: username={request.POST.get('username')}")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            logger.warning("Login failed: Missing username or password")
            return render(
                request, "login.html",
                {"form": {}, "error": "Username and Password are required."}
            )

        try:
            # Find user by username OR roll_no or email
            try:
                user = User.objects.get(
                    Q(username=username) | 
                    Q(email=username) | 
                    Q(roll_no=username)
                )
            except User.DoesNotExist:
                user = None

            # Validate password
            if user and user.check_password(password):
                logger.info(f"User '{username}' authenticated successfully.")
                login(request, user)

                # Role-based redirection
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

                for r in ['ADMIN', 'SAC_COORDINATOR']:
                    if r in roles:
                        return redirect(role_map[r])

                for r_key, view_name in role_map.items():
                    if r_key in roles:
                        return redirect(view_name)

                return redirect("student-dashboard")

            else:
                logger.warning(f"Invalid login attempt for '{username}'")
                return render(
                    request, "login.html",
                    {"form": {}, "error": "Invalid username or password."}
                )

        except Exception as e:
            logger.exception("Error during authentication:")
            return render(
                request, "login.html",
                {"form": {}, "error": f"Internal error: {str(e)}"}
            )

    logger.debug("Rendering login page.")
    return render(request, "login.html", {"form": {}})


def logout_view(request):
    logout(request)
    return redirect("login")
