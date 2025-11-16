from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count
from users.models import Club, Department, User

def club_list(request):
    """List all clubs"""
    clubs = Club.objects.all().prefetch_related('coordinators', 'members', 'events')
    
    # Add counts
    clubs = clubs.annotate(
        members_count=Count('members'),
        events_count=Count('events')
    )
    
    # Pagination
    paginator = Paginator(clubs, 12)
    page_number = request.GET.get('page')
    clubs = paginator.get_page(page_number)
    
    return render(request, 'clubs/club_list.html', {'clubs': clubs})

def club_detail(request, club_id):
    """Display club details"""
    club = get_object_or_404(Club, id=club_id)
    
    # Get recent events
    recent_events = club.events.all().order_by('-date_time')[:5]
    
    context = {
        'club': club,
        'recent_events': recent_events,
    }
    return render(request, 'clubs/club_detail.html', context)

@login_required
def club_create(request):
    """Create a new club"""
    if not ('ADMIN' in request.user.roles):
        messages.error(request, 'You do not have permission to create clubs.')
        return redirect('club_list')
    
    if request.method == 'POST':
        try:
            club = Club.objects.create(
                name=request.POST['name'],
                description=request.POST.get('description', ''),
            )
            
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
    return render(request, 'clubs/club_form.html', context)

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
    return render(request, 'clubs/club_form.html', context)

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
    
    return render(request, 'clubs/club_confirm_delete.html', {'club': club})