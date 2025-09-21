from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Count
from .models import Event, CollaborationRequest
from users.models import Club, Department, User
from attendance.models import Attendance
from datetime import datetime

def event_list(request):
    """List all events with filtering options"""
    events = Event.objects.all().select_related('club', 'department').prefetch_related('organizers')
    clubs = Club.objects.all()
    
    # Filter events based on user role
    if request.user.is_authenticated:
        user_roles = request.user.roles or []
        
        # If user is a regular student (no special roles), only show approved events
        if not any(role in user_roles for role in ['FACULTY', 'CLUB_ADVISOR', 'CLUB_COORDINATOR', 'ADMIN', 'SAC_COORDINATOR', 'PRESIDENT', 'SECRETARY', 'TREASURER', 'EVENT_ORGANIZER', 'STUDENT_VOLUNTEER']):
            events = events.filter(status='APPROVED')
        # If user has management roles, they can see events based on their permissions
        elif 'ADMIN' in user_roles or 'SAC_COORDINATOR' in user_roles:
            # Admins can see all events
            pass
        elif 'FACULTY' in user_roles or 'CLUB_ADVISOR' in user_roles:
            # Faculty can see all events from clubs they advise + approved events from others
            advised_clubs = request.user.advised_clubs.all()
            events = events.filter(
                Q(club__in=advised_clubs) | Q(status='APPROVED')
            )
        elif 'CLUB_COORDINATOR' in user_roles:
            # Coordinators can see all events from clubs they coordinate + approved events from others
            coordinated_clubs = request.user.coordinated_clubs.all()
            events = events.filter(
                Q(club__in=coordinated_clubs) | Q(status='APPROVED')
            )
        else:
            # Other roles (student positions) see approved events + events they organize
            events = events.filter(
                Q(status='APPROVED') | Q(organizers=request.user)
            )
    else:
        # Anonymous users only see approved events
        events = events.filter(status='APPROVED')
    
    # Apply additional filters
    status_filter = request.GET.get('status')
    club_filter = request.GET.get('club')
    event_type_filter = request.GET.get('event_type')
    
    if status_filter:
        events = events.filter(status=status_filter)
    if club_filter:
        events = events.filter(club_id=club_filter)
    if event_type_filter:
        events = events.filter(event_type__icontains=event_type_filter)
    
    # Order by date (upcoming first)
    events = events.order_by('date_time')
    
    # Pagination
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    events = paginator.get_page(page_number)
    
    context = {
        'events': events,
        'clubs': clubs,
    }
    return render(request, 'events/event_list.html', context)

def event_detail(request, event_id):
    """Display event details"""
    event = get_object_or_404(Event, id=event_id)
    
    # Get attendance statistics if event is approved/completed
    attendance_count = None
    if event.status in ['APPROVED', 'COMPLETED']:
        attendance_count = {
            'present': Attendance.objects.filter(event=event, status='PRESENT').count(),
            'absent': Attendance.objects.filter(event=event, status='ABSENT').count(),
        }
    
    context = {
        'event': event,
        'attendance_count': attendance_count,
    }
    return render(request, 'events/event_detail.html', context)

@login_required
def event_create(request):
    """Create a new event - Only Faculty advisors and Club Coordinators allowed"""
    # Check if user has permission to create events
    can_create_event = False
    user_clubs = []
    
    # Check if user is Faculty advisor
    if 'FACULTY' in (request.user.roles or []) or 'CLUB_ADVISOR' in (request.user.roles or []):
        can_create_event = True
        # Get clubs they advise
        user_clubs = request.user.advised_clubs.all()
    
    # Check if user is Club Coordinator
    elif 'CLUB_COORDINATOR' in (request.user.roles or []):
        can_create_event = True
        # Get clubs they coordinate
        user_clubs = request.user.coordinated_clubs.all()
    
    # Allow admins to create events too
    elif 'ADMIN' in (request.user.roles or []) or 'SAC_COORDINATOR' in (request.user.roles or []):
        can_create_event = True
        user_clubs = Club.objects.all()
    
    if not can_create_event:
        messages.error(request, 'You do not have permission to create events. Only Faculty advisors, Club Coordinators, and Administrators can create events.')
        return redirect('event_list')
    
    if request.method == 'POST':
        try:
            # Debug: Print form data
            print("Form data:", request.POST)
            
            # Validate required fields
            required_fields = ['name', 'event_type', 'date_time', 'venue', 'club']
            missing_fields = []
            for field in required_fields:
                if not request.POST.get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                messages.error(request, f'Missing required fields: {", ".join(missing_fields)}')
                
                # Check if user is a club coordinator with single club
                is_club_coordinator = 'CLUB_COORDINATOR' in (request.user.roles or [])
                coordinator_club = None
                if is_club_coordinator and user_clubs.count() == 1:
                    coordinator_club = user_clubs.first()
                
                return render(request, 'events/event_form.html', {
                    'clubs': user_clubs if user_clubs.exists() else Club.objects.all(),
                    'departments': Department.objects.all(),
                    'can_create_event': can_create_event,
                    'user_role': 'Faculty Advisor' if 'FACULTY' in (request.user.roles or []) else 'Club Coordinator' if 'CLUB_COORDINATOR' in (request.user.roles or []) else 'Administrator',
                    'is_club_coordinator': is_club_coordinator,
                    'coordinator_club': coordinator_club,
                    'form': request.POST,
                })
            
            # Create event from form data
            # Set status based on user role
            event_status = 'PENDING'  # Default: needs approval
            if 'ADMIN' in (request.user.roles or []) or 'SAC_COORDINATOR' in (request.user.roles or []):
                event_status = 'APPROVED'  # Admins can auto-approve
            
            event = Event.objects.create(
                name=request.POST['name'],
                event_type=request.POST['event_type'],
                description=request.POST.get('description', ''),
                date_time=request.POST['date_time'],
                venue=request.POST['venue'],
                club_id=request.POST['club'],
                department_id=request.POST.get('department') or None,
                resources=request.POST.get('resources', ''),
                status=event_status,
                created_by=request.user
            )
            
            # Add organizers - automatically set to club coordinators
            selected_club = Club.objects.get(id=request.POST['club'])
            event.organizers.set(selected_club.coordinators.all())
            
            # Also add the event creator as an organizer if they're not already included
            if request.user not in selected_club.coordinators.all():
                event.organizers.add(request.user)
            
            if event_status == 'PENDING':
                messages.success(request, f'Event "{event.name}" created successfully and submitted for administrator approval!')
            else:
                messages.success(request, f'Event "{event.name}" created and approved successfully!')
            return redirect('event_detail', event_id=event.id)
            
        except Exception as e:
            messages.error(request, f'Error creating event: {str(e)}')
    
    # Get form data
    clubs = user_clubs if user_clubs.exists() else Club.objects.all()
    departments = Department.objects.all()
    
    # Check if user is a club coordinator with single club
    is_club_coordinator = 'CLUB_COORDINATOR' in (request.user.roles or [])
    coordinator_club = None
    if is_club_coordinator and user_clubs.count() == 1:
        coordinator_club = user_clubs.first()
    
    context = {
        'clubs': clubs,
        'departments': departments,
        'can_create_event': can_create_event,
        'user_role': 'Faculty Advisor' if 'FACULTY' in (request.user.roles or []) else 'Club Coordinator' if 'CLUB_COORDINATOR' in (request.user.roles or []) else 'Administrator',
        'is_club_coordinator': is_club_coordinator,
        'coordinator_club': coordinator_club,
    }
    return render(request, 'events/event_form.html', context)

@login_required
def event_edit(request, event_id):
    """Edit an existing event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check permissions - only Faculty advisors, Club Coordinators, organizers, and admins can edit
    can_edit = False
    
    # Check if user is admin/SAC coordinator
    if 'ADMIN' in (request.user.roles or []) or 'SAC_COORDINATOR' in (request.user.roles or []):
        can_edit = True
    # Check if user is Faculty advisor of the club
    elif 'FACULTY' in (request.user.roles or []) and event.club.advisor == request.user:
        can_edit = True
    # Check if user is Club Coordinator of the club
    elif 'CLUB_COORDINATOR' in (request.user.roles or []) and request.user in event.club.coordinators.all():
        can_edit = True
    # Check if user is an organizer
    elif request.user in event.organizers.all():
        can_edit = True
    
    if not can_edit:
        messages.error(request, 'You do not have permission to edit this event. Only Faculty advisors, Club Coordinators, event organizers, and Administrators can edit events.')
        return redirect('event_detail', event_id=event.id)
    
    if request.method == 'POST':
        try:
            # Update event
            event.name = request.POST['name']
            event.event_type = request.POST['event_type']
            event.description = request.POST.get('description', '')
            event.date_time = request.POST['date_time']
            event.venue = request.POST['venue']
            event.club_id = request.POST['club']
            event.department_id = request.POST.get('department') or None
            event.resources = request.POST.get('resources', '')
            
            # Update status if user has permission
            if 'status' in request.POST and (request.user.is_staff or 'ADMIN' in request.user.roles):
                event.status = request.POST['status']
            
            event.save()
            
            # Update organizers - automatically set to club coordinators
            selected_club = Club.objects.get(id=request.POST['club'])
            event.organizers.set(selected_club.coordinators.all())
            
            # Also add the event creator as an organizer if they're not already included
            if event.created_by and event.created_by not in selected_club.coordinators.all():
                event.organizers.add(event.created_by)
            
            messages.success(request, f'Event "{event.name}" updated successfully!')
            return redirect('event_detail', event_id=event.id)
            
        except Exception as e:
            messages.error(request, f'Error updating event: {str(e)}')
    
    # Get form data
    clubs = Club.objects.all()
    departments = Department.objects.all()
    
    # Check if user is a club coordinator
    is_club_coordinator = 'CLUB_COORDINATOR' in (request.user.roles or [])
    coordinator_club = None
    if is_club_coordinator:
        user_coordinated_clubs = request.user.coordinated_clubs.all()
        if user_coordinated_clubs.count() == 1:
            coordinator_club = user_coordinated_clubs.first()
    
    context = {
        'event': event,
        'clubs': clubs,
        'departments': departments,
        'is_club_coordinator': is_club_coordinator,
        'coordinator_club': coordinator_club,
    }
    return render(request, 'events/event_form.html', context)

@login_required
def event_delete(request, event_id):
    """Delete an event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check permissions
    if not (request.user.is_staff or 'ADMIN' in request.user.roles):
        messages.error(request, 'You do not have permission to delete events.')
        return redirect('event_detail', event_id=event.id)
    
    if request.method == 'POST':
        event_name = event.name
        event.delete()
        messages.success(request, f'Event "{event_name}" deleted successfully!')
        return redirect('event_list')
    
    return render(request, 'events/event_confirm_delete.html', {'event': event})