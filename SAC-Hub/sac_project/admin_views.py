from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from users.models import User, Club, Role
import json

@login_required
def assign_club_coordinator(request):
    """View for SAC Coordinators to assign club coordinators"""
    # Check if user is SAC Coordinator
    if 'SAC_COORDINATOR' not in request.user.roles and 'ADMIN' not in request.user.roles:
        messages.error(request, 'You do not have permission to assign club coordinators.')
        return redirect('student-dashboard')
    
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_id')
            club_id = request.POST.get('club_id')
            action = request.POST.get('action')  # 'add' or 'remove'
            
            student = get_object_or_404(User, id=student_id)
            club = get_object_or_404(Club, id=club_id)
            
            if action == 'add':
                # Add CLUB_COORDINATOR role if not present
                if 'CLUB_COORDINATOR' not in student.roles:
                    student.roles.append('CLUB_COORDINATOR')
                    student.save()
                
                # Add student as club coordinator
                club.coordinators.add(student)
                messages.success(request, f'{student.get_full_name()} has been assigned as coordinator for {club.name}')
                
            elif action == 'remove':
                # Remove student from club coordinators
                club.coordinators.remove(student)
                
                # If student is not coordinator of any other club, remove CLUB_COORDINATOR role
                if not student.coordinated_clubs.exists():
                    if 'CLUB_COORDINATOR' in student.roles:
                        student.roles.remove('CLUB_COORDINATOR')
                        student.save()
                
                messages.success(request, f'{student.get_full_name()} has been removed as coordinator for {club.name}')
            
            return redirect('assign_club_coordinator')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    # Get all students and clubs for the form
    # Filter students with STUDENT role (SQLite-compatible)
    all_users = User.objects.all().order_by('first_name', 'last_name')
    students = [user for user in all_users if 'STUDENT' in (user.roles or [])]
    clubs = Club.objects.all().order_by('name')
    
    # Get current coordinator assignments
    coordinator_assignments = []
    for club in clubs:
        for coordinator in club.coordinators.all():
            coordinator_assignments.append({
                'club': club,
                'coordinator': coordinator
            })
    
    context = {
        'students': students,
        'clubs': clubs,
        'coordinator_assignments': coordinator_assignments,
    }
    
    return render(request, 'admin/assign_club_coordinator.html', context)

@login_required
@require_http_methods(['GET'])
def get_students_ajax(request):
    """AJAX endpoint to get students for dropdown"""
    if 'SAC_COORDINATOR' not in request.user.roles and 'ADMIN' not in request.user.roles:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    search_term = request.GET.get('q', '')
    # Filter students without club coordinator role (SQLite-compatible)
    all_users = User.objects.all()
    students = [
        user for user in all_users 
        if 'STUDENT' in (user.roles or []) and 'CLUB_COORDINATOR' not in (user.roles or [])
    ]
    
    if search_term:
        # Apply search filter to the Python-filtered list
        students = [
            student for student in students
            if (search_term.lower() in (student.first_name or '').lower() or
                search_term.lower() in (student.last_name or '').lower() or
                search_term.lower() in (student.roll_no or '').lower())
        ]
    
    students_data = [
        {
            'id': student.id,
            'name': student.get_full_name(),
            'roll_no': student.roll_no,
            'email': student.email
        }
        for student in students[:20]  # Limit to 20 results
    ]
    
    return JsonResponse({'students': students_data})