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
    
    # Apply filters
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
    """Create a new event"""
    if request.method == 'POST':
        try:
            # Create event from form data
            event = Event.objects.create(
                name=request.POST['name'],
                event_type=request.POST['event_type'],
                description=request.POST.get('description', ''),
                date_time=request.POST['date_time'],
                venue=request.POST['venue'],
                club_id=request.POST['club'],
                department_id=request.POST.get('department') or None,
                resources=request.POST.get('resources', ''),
                status='DRAFT'
            )
            
            # Add organizers
            organizer_ids = request.POST.getlist('organizers')
            if organizer_ids:
                event.organizers.set(organizer_ids)
            
            messages.success(request, f'Event "{event.name}" created successfully!')
            return redirect('event_detail', event_id=event.id)
            
        except Exception as e:
            messages.error(request, f'Error creating event: {str(e)}')
    
    # Get form data
    clubs = Club.objects.all()
    departments = Department.objects.all()
    users = User.objects.filter(is_active=True)
    
    context = {
        'clubs': clubs,
        'departments': departments,
        'users': users,
    }
    return render(request, 'events/event_form.html', context)

@login_required
def event_edit(request, event_id):
    """Edit an existing event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check permissions
    if not (request.user in event.organizers.all() or 
            request.user in event.club.coordinators.all() or 
            'ADMIN' in request.user.roles):
        messages.error(request, 'You do not have permission to edit this event.')
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
            
            # Update organizers
            organizer_ids = request.POST.getlist('organizers')
            event.organizers.set(organizer_ids)
            
            messages.success(request, f'Event "{event.name}" updated successfully!')
            return redirect('event_detail', event_id=event.id)
            
        except Exception as e:
            messages.error(request, f'Error updating event: {str(e)}')
    
    # Get form data
    clubs = Club.objects.all()
    departments = Department.objects.all()
    users = User.objects.filter(is_active=True)
    
    context = {
        'event': event,
        'clubs': clubs,
        'departments': departments,
        'users': users,
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