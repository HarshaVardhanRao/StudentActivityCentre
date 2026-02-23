from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count
from users.models import Club, Department, User

from django.core.paginator import Paginator
from django.db.models import Count

from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render


def club_list(request):
    """List all clubs with pagination and joined status"""
    # Use the correct M2M reverse name: 'members'
    clubs = Club.objects.all().prefetch_related('coordinators', 'events', 'members')

    # Annotate counts
    clubs = clubs.annotate(
        members_count=Count('members'),  # Correct field name
        events_count=Count('events')
    )

    # Get IDs of clubs the current user has joined
    joined_club_ids = []
    if request.user.is_authenticated:
        joined_club_ids = request.user.clubs.values_list('id', flat=True)

    # Pagination
    paginator = Paginator(clubs, 12)
    page_number = request.GET.get('page')
    clubs_page = paginator.get_page(page_number)

    return render(request, 'clubs_list.html', {
        'clubs': clubs_page,
        'joined_club_ids': joined_club_ids
    })



def club_detail(request, club_id):
    """Display club details"""
    club = get_object_or_404(Club, id=club_id)
    
    # Get recent events
    recent_events = club.events.all().order_by('-date_time')[:5]
    
    context = {
        'club': club,
        'recent_events': recent_events,
    }
    return render(request, 'clubs_detail.html', context)

@login_required
def club_create(request):
    """Create a new club"""
    if not ('SAC_COORDINATOR' in request.user.roles):
        messages.error(request, 'You do not have permission to create clubs.')
        return redirect('club_list')
    
    if request.method == 'POST':
        try:
            club = Club.objects.create(
                name=request.POST['name'],
                description=request.POST.get('description', ''),
            )
            
            # Handle certificate template upload
            if 'certificate_template' in request.FILES:
                club.certificate_template = request.FILES['certificate_template']
                club.save()
            
            # Add coordinators (signals will handle role assignment)
            coordinator_ids = request.POST.getlist('coordinators')
            if coordinator_ids:
                club.coordinators.set(coordinator_ids)
            
            # Add advisor
            advisor_id = request.POST.get('advisor')
            if advisor_id:
                club.advisor_id = advisor_id
                club.save()
            
            messages.success(request, f'Club "{club.name}" created successfully!')
            return redirect('club_detail', club_id=club.id)
            
        except Exception as e:
            messages.error(request, f'Error creating club: {str(e)}')
    
    # Get users for coordinators and advisors (SQLite compatible)
    all_users = User.objects.filter(is_active=True)
    faculty_users = [user for user in all_users if 'FACULTY' in (user.roles or [])]
    
    context = {
        'faculty_users': faculty_users,
        'all_users': all_users,
    }
    return render(request, 'clubs_form.html', context)

@login_required
def club_edit(request, club_id):
    """Edit an existing club"""
    club = get_object_or_404(Club, id=club_id)
    
    # Check permissions
    if not (request.user in club.coordinators.all() or 'ADMIN' in request.user.roles):
        messages.error(request, 'You do not have permission to edit this club.')
        return redirect('club_detail', club_id=club.id)
    
    if request.method == 'POST':
        try:
            club.name = request.POST['name']
            club.description = request.POST.get('description', '')
            
            # Handle certificate template upload
            if 'certificate_template' in request.FILES:
                club.certificate_template = request.FILES['certificate_template']
            
            # Update advisor
            advisor_id = request.POST.get('advisor')
            if advisor_id:
                club.advisor_id = advisor_id
            else:
                club.advisor = None
            
            club.save()
            
            # Update coordinators (signals will handle role assignment)
            coordinator_ids = request.POST.getlist('coordinators')
            club.coordinators.set(coordinator_ids)
            
            messages.success(request, f'Club "{club.name}" updated successfully!')
            return redirect('club_detail', club_id=club.id)
            
        except Exception as e:
            messages.error(request, f'Error updating club: {str(e)}')
    
    # Get users for coordinators and advisors (SQLite compatible)
    all_users = User.objects.filter(is_active=True)
    faculty_users = [user for user in all_users if 'FACULTY' in (user.roles or [])]
    
    context = {
        'club': club,
        'faculty_users': faculty_users,
        'all_users': all_users,
    }
    return render(request, 'clubs_form.html', context)

@login_required
def club_join(request, club_id):
    """Join a club"""
    club = get_object_or_404(Club, id=club_id)
    
    if request.user in club.members.all():
        messages.info(request, f'You are already a member of {club.name}.')
    else:
        club.members.add(request.user)
        messages.success(request, f'You have successfully joined {club.name}!')
    
    return redirect('club_detail', club_id=club.id)

@login_required
def club_leave(request, club_id):
    """Leave a club"""
    club = get_object_or_404(Club, id=club_id)
    
    if request.user not in club.members.all():
        messages.info(request, f'You are not a member of {club.name}.')
    else:
        club.members.remove(request.user)
        messages.success(request, f'You have left {club.name}.')
    
    return redirect('club_detail', club_id=club.id)

@login_required
def club_delete(request, club_id):
    """Delete a club"""
    club = get_object_or_404(Club, id=club_id)
    
    # Check permissions - only admins can delete
    if not ('ADMIN' in request.user.roles or request.user.is_staff):
        messages.error(request, 'You do not have permission to delete clubs.')
        return redirect('club_detail', club_id=club.id)
    
    if request.method == 'POST':
        club_name = club.name
        club.delete()
        messages.success(request, f'Club "{club_name}" deleted successfully!')
        return redirect('club_list')
    
    return render(request, 'clubs_confirm_delete.html', {'club': club})

@login_required
def manage_club_members(request, club_id):
    """Manage club members - view, filter, edit members"""
    club = get_object_or_404(Club, id=club_id)
    
    # Check permissions - only club coordinators of this club can manage members
    user_roles = request.user.roles or []
    is_coordinator = 'CLUB_COORDINATOR' in user_roles and request.user in club.coordinators.all()
    is_admin = 'ADMIN' in user_roles or 'SAC_COORDINATOR' in user_roles
    is_advisor = 'CLUB_ADVISOR' in user_roles and club.advisor == request.user
    
    if not (is_coordinator or is_admin or is_advisor):
        messages.error(request, 'You do not have permission to manage this club\'s members.')
        return redirect('club_detail', club_id=club.id)
    
    # Get members
    members = club.members.all().select_related('department')
    
    # Search filter
    search_query = request.GET.get('search', '').strip()
    if search_query:
        from django.db.models import Q
        members = members.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(roll_no__icontains=search_query) |
            Q(username__icontains=search_query)
        )
    
    # Role filter
    role_filter = request.GET.get('role', '').strip()
    if role_filter:
        # Filter users by JSON array containment
        members = members.filter(roles__contains=role_filter)
    
    # Department filter
    dept_filter = request.GET.get('department', '').strip()
    if dept_filter:
        members = members.filter(department_id=dept_filter)
    
    # Year filter
    year_filter = request.GET.get('year', '').strip()
    if year_filter:
        members = members.filter(year_of_study=year_filter)
    
    # Sort
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'date_joined':
        members = members.order_by('-date_joined')
    elif sort_by == 'email':
        members = members.order_by('email')
    else:
        members = members.order_by('first_name', 'last_name')
    
    # Handle member removal
    if request.method == 'POST':
        action = request.POST.get('action')
        member_id = request.POST.get('member_id')
        
        if action == 'remove':
            try:
                member = User.objects.get(id=member_id)
                if member in club.members.all():
                    club.members.remove(member)
                    messages.success(request, f'{member.get_full_name()} has been removed from {club.name}.')
                else:
                    messages.warning(request, f'{member.get_full_name()} is not a member of {club.name}.')
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
            return redirect('manage_club_members', club_id=club.id)
    
    # Pagination
    paginator = Paginator(members, 15)
    page_number = request.GET.get('page')
    members_page = paginator.get_page(page_number)
    
    # Get all departments for filter dropdown
    departments = Department.objects.all()
    
    # Get all years for filter dropdown
    all_years = set(User.objects.filter(clubs=club).exclude(year_of_study__isnull=True).exclude(year_of_study='').values_list('year_of_study', flat=True))
    all_years = sorted(list(all_years))
    
    context = {
        'club': club,
        'members': members_page,
        'total_members': club.members.count(),
        'search_query': search_query,
        'role_filter': role_filter,
        'dept_filter': dept_filter,
        'year_filter': year_filter,
        'sort_by': sort_by,
        'departments': departments,
        'all_years': all_years,
        'is_coordinator': is_coordinator,
        'is_admin': is_admin,
        'is_advisor': is_advisor,
    }
    
    return render(request, 'clubs/manage_members_v2.html', context)