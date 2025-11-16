from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Count
from .models import Event, CollaborationRequest
from users.models import Club, Department, User, Notification
from attendance.models import Attendance
from datetime import datetime

def event_list(request):
    """List all events with filtering options"""
    from .models import EventRegistration
    
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
    
    # Add registration counts and user registration status
    if request.user.is_authenticated:
        for event in events:
            event.registration_count = EventRegistration.objects.filter(event=event).count()
            event.user_registered = EventRegistration.objects.filter(event=event, student=request.user).exists()
    
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
    from .models import EventRegistration
    
    event = get_object_or_404(Event, id=event_id)
    
    # Prefetch associations and collaborations. If the related tables are missing
    # (e.g. migrations haven't been applied yet) fall back to a safer query
    # to avoid a server 500 and give the operator time to run migrations.
    try:
        event = Event.objects.select_related('club', 'department').prefetch_related(
            'organizers',
            'associations__department',
            'associations__club', 
            'collaborations__department',
            'collaborations__club'
        ).get(id=event_id)
    except Exception as e:
        # Import here to avoid top-level import if Django isn't fully available
        from django.db import utils as db_utils
        # If the error is an OperationalError (missing table), fall back to a query
        if isinstance(e, db_utils.OperationalError):
            event = Event.objects.select_related('club', 'department').prefetch_related('organizers').get(id=event_id)
        else:
            raise
    
    # Get attendance statistics if event is approved/completed
    attendance_count = None
    if event.status in ['APPROVED', 'COMPLETED']:
        attendance_count = {
            'present': Attendance.objects.filter(event=event, status='PRESENT').count(),
            'absent': Attendance.objects.filter(event=event, status='ABSENT').count(),
        }
    
    # Check registration status for logged-in users
    user_registered = False
    user_registration = None
    registration_count = 0
    can_view_registrations = False
    
    if request.user.is_authenticated:
        user_registration = EventRegistration.objects.filter(event=event, student=request.user).first()
        user_registered = user_registration is not None
        
        # Check if user can view registrations
        user_roles = request.user.roles or []
        if ('ADMIN' in user_roles or 'SAC_COORDINATOR' in user_roles or 
            request.user in event.organizers.all() or
            (event.club and 'FACULTY' in user_roles and event.club.advisor == request.user) or
            (event.club and 'CLUB_COORDINATOR' in user_roles and request.user in event.club.coordinators.all())):
            can_view_registrations = True
    
    # Get registration count only for authorized users
    if can_view_registrations:
        registration_count = EventRegistration.objects.filter(event=event).count()
    
    context = {
        'event': event,
        'attendance_count': attendance_count,
        'user_registered': user_registered,
        'user_registration': user_registration,
        'registration_count': registration_count,
        'can_view_registrations': can_view_registrations,
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
            
            # Validate required fields (club is now optional)
            required_fields = ['name', 'event_type', 'date_time', 'venue']
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
                    'all_clubs': Club.objects.all(),
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
            
            club_id = request.POST.get('club') or None
            
            event = Event.objects.create(
                name=request.POST['name'],
                event_type=request.POST['event_type'],
                description=request.POST.get('description', ''),
                date_time=request.POST['date_time'],
                venue=request.POST['venue'],
                club_id=club_id,
                department_id=request.POST.get('department') or None,
                resources=request.POST.get('resources', ''),
                status=event_status,
                created_by=request.user
            )
            
            # Add organizers - automatically set to club coordinators (if club is assigned)
            if club_id:
                selected_club = Club.objects.get(id=club_id)
                event.organizers.set(selected_club.coordinators.all())
                
                # Also add the event creator as an organizer if they're not already included
                if request.user not in selected_club.coordinators.all():
                    event.organizers.add(request.user)
            else:
                # If no club is assigned, add only the creator as organizer
                event.organizers.add(request.user)
            
            # Handle Associations
            from .models import EventAssociation, EventCollaboration
            
            # Department Associations
            dept_associations = request.POST.getlist('department_associations')
            for dept_id in dept_associations:
                if dept_id:
                    department = Department.objects.get(id=dept_id)
                    EventAssociation.objects.create(
                        event=event,
                        association_type='DEPARTMENT',
                        department=department,
                        requested_by=request.user
                    )
            
            # Club Associations
            club_associations = request.POST.getlist('club_associations')
            for club_id in club_associations:
                if club_id:
                    club = Club.objects.get(id=club_id)
                    EventAssociation.objects.create(
                        event=event,
                        association_type='CLUB',
                        club=club,
                        requested_by=request.user
                    )
            
            # Handle Collaborations
            collaboration_details = request.POST.get('collaboration_details', '')
            
            # Department Collaborations
            dept_collaborations = request.POST.getlist('department_collaborations')
            for dept_id in dept_collaborations:
                if dept_id:
                    department = Department.objects.get(id=dept_id)
                    EventCollaboration.objects.create(
                        event=event,
                        collaboration_type='DEPARTMENT',
                        department=department,
                        collaboration_details=collaboration_details,
                        requested_by=request.user
                    )
            
            # Club Collaborations
            club_collaborations = request.POST.getlist('club_collaborations')
            for club_id in club_collaborations:
                if club_id:
                    club = Club.objects.get(id=club_id)
                    EventCollaboration.objects.create(
                        event=event,
                        collaboration_type='CLUB',
                        club=club,
                        collaboration_details=collaboration_details,
                        requested_by=request.user
                    )
            
            success_message = f'Event "{event.name}" created successfully'
            if dept_associations or club_associations:
                success_message += ' with association requests'
            if dept_collaborations or club_collaborations:
                success_message += ' and collaboration requests'
            success_message += '!'
            
            if event_status == 'PENDING':
                success_message += ' Event submitted for administrator approval.'
            else:
                success_message += ' Event approved successfully!'
            
            messages.success(request, success_message)
            return redirect('event_detail', event_id=event.id)
            
        except Exception as e:
            messages.error(request, f'Error creating event: {str(e)}')
    
    # Get form data
    clubs = user_clubs if user_clubs.exists() else Club.objects.all()
    departments = Department.objects.all()
    all_clubs = Club.objects.all()  # For associations and collaborations
    
    # Check if user is a club coordinator with single club
    is_club_coordinator = 'CLUB_COORDINATOR' in (request.user.roles or [])
    coordinator_club = None
    if is_club_coordinator and user_clubs.count() == 1:
        coordinator_club = user_clubs.first()
    
    context = {
        'clubs': clubs,
        'departments': departments,
        'all_clubs': all_clubs,
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
    # Check if user is Faculty advisor of the club (if club is assigned)
    elif event.club and 'FACULTY' in (request.user.roles or []) and event.club.advisor == request.user:
        can_edit = True
    # Check if user is Club Coordinator of the club (if club is assigned)
    elif event.club and 'CLUB_COORDINATOR' in (request.user.roles or []) and request.user in event.club.coordinators.all():
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
            
            club_id = request.POST.get('club') or None
            event.club_id = club_id
            event.department_id = request.POST.get('department') or None
            event.resources = request.POST.get('resources', '')
            
            # Update status if user has permission
            if 'status' in request.POST and (request.user.is_staff or 'ADMIN' in request.user.roles):
                event.status = request.POST['status']
            
            event.save()
            
            # Update organizers - automatically set to club coordinators (if club is assigned)
            if club_id:
                selected_club = Club.objects.get(id=club_id)
                event.organizers.set(selected_club.coordinators.all())
                
                # Also add the event creator as an organizer if they're not already included
                if event.created_by and event.created_by not in selected_club.coordinators.all():
                    event.organizers.add(event.created_by)
            else:
                # If no club is assigned, keep only creator as organizer
                if event.created_by:
                    event.organizers.set([event.created_by])
                else:
                    event.organizers.clear()
            
            messages.success(request, f'Event "{event.name}" updated successfully!')
            return redirect('event_detail', event_id=event.id)
            
        except Exception as e:
            messages.error(request, f'Error updating event: {str(e)}')
    
    # Get form data
    clubs = Club.objects.all()
    departments = Department.objects.all()
    all_clubs = Club.objects.all()
    
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
        'all_clubs': all_clubs,
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

@login_required
def event_register(request, event_id):
    """Register for an event"""
    from .models import EventRegistration
    
    event = get_object_or_404(Event, id=event_id)
    
    # Check if event is approved and in the future
    if event.status != 'APPROVED':
        messages.error(request, 'You can only register for approved events.')
        return redirect('event_detail', event_id=event.id)
    
    # Check if event hasn't passed
    from django.utils import timezone
    if event.date_time < timezone.now():
        messages.error(request, 'You cannot register for past events.')
        return redirect('event_detail', event_id=event.id)
    
    # Check if user is already registered
    if EventRegistration.objects.filter(event=event, student=request.user).exists():
        messages.warning(request, 'You are already registered for this event.')
        return redirect('event_detail', event_id=event.id)
    
    if request.method == 'POST':
        try:
            registration = EventRegistration.objects.create(
                event=event,
                student=request.user,
                notes=request.POST.get('notes', '')
            )
            
            # Notify organizers about new registration
            for organizer in event.organizers.all():
                Notification.objects.create(
                    user=organizer,
                    message=f"{request.user.get_full_name()} registered for event '{event.name}'."
                )
            
            messages.success(request, f'Successfully registered for "{event.name}"!')
            return redirect('event_detail', event_id=event.id)
            
        except Exception as e:
            messages.error(request, f'Error registering for event: {str(e)}')
    
    context = {
        'event': event,
    }
    return render(request, 'events/event_register.html', context)

@login_required
def event_unregister(request, event_id):
    """Unregister from an event"""
    from .models import EventRegistration
    
    event = get_object_or_404(Event, id=event_id)
    
    try:
        registration = EventRegistration.objects.get(event=event, student=request.user)
        registration.delete()
        
        # Notify organizers about unregistration
        for organizer in event.organizers.all():
            Notification.objects.create(
                user=organizer,
                message=f"{request.user.get_full_name()} unregistered from event '{event.name}'."
            )
        
        messages.success(request, f'Successfully unregistered from "{event.name}".')
        
    except EventRegistration.DoesNotExist:
        messages.error(request, 'You are not registered for this event.')
    
    return redirect('event_detail', event_id=event.id)

@login_required
def event_registrations(request, event_id):
    """View registrations for an event (for organizers)"""
    from .models import EventRegistration
    
    event = get_object_or_404(Event, id=event_id)
    
    # Check if user has permission to view registrations
    can_view = False
    user_roles = request.user.roles or []
    
    if ('ADMIN' in user_roles or 'SAC_COORDINATOR' in user_roles or 
        request.user in event.organizers.all() or
        (event.club and 'FACULTY' in user_roles and event.club.advisor == request.user) or
        (event.club and 'CLUB_COORDINATOR' in user_roles and request.user in event.club.coordinators.all())):
        can_view = True
    
    if not can_view:
        messages.error(request, 'You do not have permission to view event registrations.')
        return redirect('event_detail', event_id=event.id)
    
    registrations = EventRegistration.objects.filter(event=event).select_related('student').order_by('-registered_at')
    
    context = {
        'event': event,
        'registrations': registrations,
        'registration_count': registrations.count(),
    }
    return render(request, 'events/event_registrations.html', context)

@login_required
def association_approval_list(request):
    """View for officers to approve/reject event associations"""
    from .models import EventAssociation, EventCollaboration
    
    user_roles = request.user.roles or []
    
    # Get pending associations based on user role
    pending_associations = []
    pending_collaborations = []
    
    # Department admin can approve department associations and collaborations
    if 'DEPARTMENT_ADMIN' in user_roles and request.user.department:
        dept_associations = EventAssociation.objects.filter(
            association_type='DEPARTMENT',
            department=request.user.department,
            status='PENDING'
        ).select_related('event', 'requested_by')
        
        dept_collaborations = EventCollaboration.objects.filter(
            collaboration_type='DEPARTMENT',
            department=request.user.department,
            status='PENDING'
        ).select_related('event', 'requested_by')
        
        pending_associations.extend(dept_associations)
        pending_collaborations.extend(dept_collaborations)
    
    # Club coordinators and advisors can approve club associations and collaborations
    if 'CLUB_COORDINATOR' in user_roles:
        for club in request.user.coordinated_clubs.all():
            club_associations = EventAssociation.objects.filter(
                association_type='CLUB',
                club=club,
                status='PENDING'
            ).select_related('event', 'requested_by')
            
            club_collaborations = EventCollaboration.objects.filter(
                collaboration_type='CLUB',
                club=club,
                status='PENDING'
            ).select_related('event', 'requested_by')
            
            pending_associations.extend(club_associations)
            pending_collaborations.extend(club_collaborations)
    
    if 'CLUB_ADVISOR' in user_roles:
        for club in request.user.advised_clubs.all():
            club_associations = EventAssociation.objects.filter(
                association_type='CLUB',
                club=club,
                status='PENDING'
            ).select_related('event', 'requested_by')
            
            club_collaborations = EventCollaboration.objects.filter(
                collaboration_type='CLUB',
                club=club,
                status='PENDING'
            ).select_related('event', 'requested_by')
            
            pending_associations.extend(club_associations)
            pending_collaborations.extend(club_collaborations)
    
    context = {
        'pending_associations': pending_associations,
        'pending_collaborations': pending_collaborations,
    }
    
    return render(request, 'events/association_approval_list.html', context)

@login_required
def approve_association(request, association_id):
    """Approve or reject an event association"""
    from .models import EventAssociation
    
    association = get_object_or_404(EventAssociation, id=association_id)
    
    # Check permissions
    can_approve = False
    user_roles = request.user.roles or []
    
    if association.association_type == 'DEPARTMENT':
        if 'DEPARTMENT_ADMIN' in user_roles and request.user.department == association.department:
            can_approve = True
    else:  # CLUB
        if ('CLUB_COORDINATOR' in user_roles and request.user in association.club.coordinators.all()) or \
           ('CLUB_ADVISOR' in user_roles and request.user == association.club.advisor):
            can_approve = True
    
    if not can_approve:
        messages.error(request, 'You do not have permission to approve this association.')
        return redirect('association_approval_list')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            association.status = 'APPROVED'
            association.approved_by = request.user
            association.approval_notes = notes
            association.save()
            
            messages.success(request, f'Association with {association.get_associated_entity().name} approved.')
            
            # Notify the requester
            Notification.objects.create(
                user=association.requested_by,
                message=f"Your association request for event '{association.event.name}' with {association.get_associated_entity().name} has been approved."
            )
            
        elif action == 'reject':
            association.status = 'REJECTED'
            association.approved_by = request.user
            association.approval_notes = notes
            association.save()
            
            messages.success(request, f'Association with {association.get_associated_entity().name} rejected.')
            
            # Notify the requester
            Notification.objects.create(
                user=association.requested_by,
                message=f"Your association request for event '{association.event.name}' with {association.get_associated_entity().name} has been rejected."
            )
    
    return redirect('association_approval_list')

@login_required
def approve_collaboration(request, collaboration_id):
    """Approve or reject an event collaboration"""
    from .models import EventCollaboration
    
    collaboration = get_object_or_404(EventCollaboration, id=collaboration_id)
    
    # Check permissions
    can_approve = False
    user_roles = request.user.roles or []
    
    if collaboration.collaboration_type == 'DEPARTMENT':
        if 'DEPARTMENT_ADMIN' in user_roles and request.user.department == collaboration.department:
            can_approve = True
    else:  # CLUB
        if ('CLUB_COORDINATOR' in user_roles and request.user in collaboration.club.coordinators.all()) or \
           ('CLUB_ADVISOR' in user_roles and request.user == collaboration.club.advisor):
            can_approve = True
    
    if not can_approve:
        messages.error(request, 'You do not have permission to approve this collaboration.')
        return redirect('association_approval_list')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            collaboration.status = 'APPROVED'
            collaboration.approved_by = request.user
            collaboration.approval_notes = notes
            collaboration.save()
            
            messages.success(request, f'Collaboration with {collaboration.get_collaborating_entity().name} approved.')
            
            # Notify the requester
            Notification.objects.create(
                user=collaboration.requested_by,
                message=f"Your collaboration request for event '{collaboration.event.name}' with {collaboration.get_collaborating_entity().name} has been approved."
            )
            
        elif action == 'reject':
            collaboration.status = 'REJECTED'
            collaboration.approved_by = request.user
            collaboration.approval_notes = notes
            collaboration.save()
            
            messages.success(request, f'Collaboration with {collaboration.get_collaborating_entity().name} rejected.')
            
            # Notify the requester
            Notification.objects.create(
                user=collaboration.requested_by,
                message=f"Your collaboration request for event '{collaboration.event.name}' with {collaboration.get_collaborating_entity().name} has been rejected."
            )
    
    return redirect('association_approval_list')