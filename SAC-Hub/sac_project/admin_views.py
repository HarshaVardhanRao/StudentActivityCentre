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

@login_required
def event_approval_list(request):
    """View for administrators to see events pending approval"""
    # Check if user is admin or SAC coordinator
    if 'ADMIN' not in (request.user.roles or []) and 'SAC_COORDINATOR' not in (request.user.roles or []):
        messages.error(request, 'You do not have permission to view event approvals.')
        return redirect('student-dashboard')
    
    from events.models import Event
    
    # Get events by status
    pending_events = Event.objects.filter(status='PENDING').order_by('-created_at')
    recent_approvals = Event.objects.filter(status__in=['APPROVED', 'REJECTED']).order_by('-updated_at')[:10]
    
    context = {
        'pending_events': pending_events,
        'recent_approvals': recent_approvals,
    }
    
    return render(request, 'admin/event_approval_list.html', context)

@login_required
@require_http_methods(['POST'])
def event_approve_reject(request):
    """Approve or reject an event"""
    # Check if user is admin or SAC coordinator
    if 'ADMIN' not in (request.user.roles or []) and 'SAC_COORDINATOR' not in (request.user.roles or []):
        messages.error(request, 'You do not have permission to approve events.')
        return redirect('student-dashboard')
    
    from events.models import Event
    
    try:
        event_id = request.POST.get('event_id')
        action = request.POST.get('action')  # 'approve' or 'reject'
        notes = request.POST.get('notes', '')
        
        event = get_object_or_404(Event, id=event_id)
        
        if action == 'approve':
            event.status = 'APPROVED'
            event.approval_notes = notes
            event.save()
            messages.success(request, f'Event "{event.name}" has been approved.')
            
        elif action == 'reject':
            event.status = 'REJECTED'
            event.approval_notes = notes
            event.save()
            messages.success(request, f'Event "{event.name}" has been rejected.')
            
        else:
            messages.error(request, 'Invalid action.')
            
    except Exception as e:
        messages.error(request, f'Error processing approval: {str(e)}')
    
    return redirect('event_approval_list')