from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import calendar
import json

from events.models import Event
from events.models import EventRegistration
from attendance.models import Attendance
from calendar_app.models import CalendarEntry
from users.models import User, Club

def calendar_view(request):
    """Display calendar view with approved events - accessible to everyone"""
    # Get month and year from request
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))
    
    # Create date objects
    current_month = datetime(year, month, 1)
    
    # Calculate previous and next months
    if month == 1:
        prev_month = datetime(year - 1, 12, 1)
    else:
        prev_month = datetime(year, month - 1, 1)
    
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    
    # Get approved events for the month (visible to everyone)
    month_start = current_month
    month_end = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59, 59)
    
    approved_events = Event.objects.filter(
        date_time__range=[month_start, month_end],
        status='APPROVED'
    ).select_related('club', 'department').prefetch_related('organizers')
    
    # Add registration counts for authenticated users
    if request.user.is_authenticated:
        for event in approved_events:
            event.registration_count = EventRegistration.objects.filter(event=event).count()
            event.user_registered = EventRegistration.objects.filter(event=event, student=request.user).exists()
    
    # Create calendar structure
    cal = calendar.monthcalendar(year, month)
    calendar_weeks = []
    
    for week in cal:
        calendar_week = []
        for day in week:
            if day == 0:
                # Previous/next month day
                calendar_week.append({
                    'day': '',
                    'is_other_month': True,
                    'is_today': False,
                    'events': []
                })
            else:
                day_date = datetime(year, month, day)
                is_today = day_date.date() == datetime.now().date()
                
                # Get events for this day
                day_events = [event for event in approved_events 
                             if event.date_time.day == day]
                
                calendar_week.append({
                    'day': day,
                    'is_other_month': False,
                    'is_today': is_today,
                    'events': day_events
                })
        calendar_weeks.append(calendar_week)
    
    # Get upcoming events for the next 30 days (for sidebar)
    from django.utils import timezone
    upcoming_events = Event.objects.filter(
        date_time__gte=timezone.now(),
        date_time__lt=timezone.now() + timedelta(days=30),
        status='APPROVED'
    ).select_related('club').order_by('date_time')[:10]
    
    # Add registration info to upcoming events
    if request.user.is_authenticated:
        for event in upcoming_events:
            event.registration_count = EventRegistration.objects.filter(event=event).count()
            event.user_registered = EventRegistration.objects.filter(event=event, student=request.user).exists()
    
    context = {
        'current_month': current_month,
        'prev_month': prev_month,
        'next_month': next_month,
        'calendar_weeks': calendar_weeks,
        'upcoming_events': upcoming_events,
        'total_events_this_month': approved_events.count(),
    }
    return render(request, 'calendar/calendar_view.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
def attendance_manage(request, event_id):
    """Manage attendance for an event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Check permissions
    if not (request.user in event.organizers.all() or 
            request.user in event.club.coordinators.all() or 
            'ADMIN' in request.user.roles):
        messages.error(request, 'You do not have permission to manage attendance for this event.')
        return redirect('event_detail', event_id=event.id)
    
    if request.method == 'POST':
        # Handle AJAX attendance updates
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                
                for student_id, status in data.items():
                    student = User.objects.get(id=student_id)
                    attendance, created = Attendance.objects.get_or_create(
                        event=event,
                        student=student,
                        defaults={'status': status}
                    )
                    if not created:
                        attendance.status = status
                        attendance.save()
                
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
    
    # Get all students who could attend (club members or all students)
    if event.club:
        students = event.club.members.all()
    else:
        # Get all users and filter for students (SQLite compatible)
        all_users = User.objects.all()
        students = [user for user in all_users if 'STUDENT' in (user.roles or [])]
        # Convert to queryset-like object for template compatibility
        student_ids = [user.id for user in students]
        students = User.objects.filter(id__in=student_ids)
    
    # Get existing attendance records
    attendances = Attendance.objects.filter(event=event)
    attendance_dict = {att.student_id: att for att in attendances}
    
    # Calculate statistics
    total_students = students.count()
    present_count = attendances.filter(status='PRESENT').count()
    absent_count = attendances.filter(status='ABSENT').count()
    
    attendance_stats = {
        'total': total_students,
        'present': present_count,
        'absent': absent_count,
        'percentage': (present_count / total_students * 100) if total_students > 0 else 0
    }
    
    context = {
        'event': event,
        'students': students,
        'attendance_dict': attendance_dict,
        'attendance_stats': attendance_stats,
    }
    return render(request, 'attendance/attendance_manage.html', context)

@login_required
def profile_view(request):
    """Display user profile"""
    user = request.user
    
    if request.method == 'POST':
        try:
            # Update profile information
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.contact_number = request.POST.get('contact_number', '')
            
            # Update academic information for students
            if 'STUDENT' in (user.roles or []):
                user.year_of_study = request.POST.get('year_of_study', '')
                user.section = request.POST.get('section', '')
            
            user.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    # Get user statistics
    organized_events_count = user.organized_events.count()
    attended_events_count = user.attendances.filter(status='PRESENT').count()
    club_memberships_count = user.clubs.count()
    
    # Get recent activities
    recent_activities = []
    
    # Add organized events
    for event in user.organized_events.all()[:5]:
        recent_activities.append({
            'event': event,
            'role': 'organizer'
        })
    
    # Add attended events
    for attendance in user.attendances.filter(status='PRESENT')[:5]:
        recent_activities.append({
            'event': attendance.event,
            'role': 'attendee'
        })
    
    # Sort by date
    recent_activities.sort(key=lambda x: x['event'].date_time, reverse=True)
    recent_activities = recent_activities[:10]
    
    context = {
        'organized_events_count': organized_events_count,
        'attended_events_count': attended_events_count,
        'club_memberships_count': club_memberships_count,
        'recent_activities': recent_activities,
    }
    return render(request, 'users/profile.html', context)

@login_required
def notifications_list(request):
    """List user notifications"""
    user = request.user
    filter_type = request.GET.get('filter', 'all')
    
    # Get notifications based on filter
    notifications = user.notifications.all()
    
    if filter_type == 'unread':
        notifications = notifications.filter(read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(read=True)
    
    notifications = notifications.order_by('-created_at')
    
    # Get counts
    total_count = user.notifications.count()
    unread_count = user.notifications.filter(read=False).count()
    read_count = user.notifications.filter(read=True).count()
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    context = {
        'notifications': notifications,
        'filter': filter_type,
        'total_count': total_count,
        'unread_count': unread_count,
        'read_count': read_count,
    }
    return render(request, 'notifications/notifications_list.html', context)

@login_required
def settings_view(request):
    """User settings page"""
    return render(request, 'users/settings.html')

@login_required 
def reports_dashboard(request):
    """Reports and analytics dashboard"""
    # Check permissions
    if not ('ADMIN' in request.user.roles or 'SAC_COORDINATOR' in request.user.roles):
        messages.error(request, 'You do not have permission to view reports.')
        return redirect('student-dashboard')
    
    # This is a placeholder - you would implement actual reporting logic here
    # Calculate total students (SQLite compatible)
    all_users = User.objects.all()
    total_students = len([user for user in all_users if 'STUDENT' in (user.roles or [])])
    
    context = {
        'stats': {
            'total_events': Event.objects.count(),
            'total_participants': total_students,
            'active_clubs': Club.objects.count(),
            'avg_attendance': 75.0,  # Placeholder
        }
    }
    return render(request, 'reports/dashboard.html', context)

@login_required
def send_notification(request):
    """Send notifications to user groups based on role permissions"""
    from users.models import Notification, Department
    from django.db.models import Q
    
    user = request.user
    user_roles = user.roles if isinstance(user.roles, list) else []
    
    # Check if user has permission to send notifications
    allowed_roles = ['ADMIN', 'SAC_COORDINATOR', 'CLUB_COORDINATOR', 'CLUB_ADVISOR', 
                     'DEPARTMENT_ADMIN', 'DEPARTMENT_VP', 'EVENT_ORGANIZER', 
                     'PRESIDENT', 'SVP', 'SECRETARY', 'TREASURER']
    
    if not any(role in user_roles for role in allowed_roles):
        messages.error(request, 'You do not have permission to send notifications.')
        return redirect('student-dashboard')
    
    # Initialize context with available options based on user role
    context = {
        'user_role': user_roles[0] if user_roles else 'STUDENT',
        'recipient_options': [],
        'scope_options': [],
    }
    
    # Determine available recipient and scope options based on role
    if 'ADMIN' in user_roles or 'SAC_COORDINATOR' in user_roles:
        # Admin/SAC can send to everyone
        context['recipient_options'] = [
            ('all', 'All Users'),
            ('all_students', 'All Students'),
            ('all_faculty', 'All Faculty'),
            ('all_coordinators', 'All Club Coordinators'),
            ('all_advisors', 'All Club Advisors'),
            ('specific_club', 'Specific Club'),
            ('specific_department', 'Specific Department'),
        ]
        context['scope_options'] = []
        
    elif 'CLUB_COORDINATOR' in user_roles:
        # Club coordinator can send to their club members
        coordinator_clubs = user.coordinated_clubs.all()
        context['recipient_options'] = [
            ('club_members', 'My Club Members'),
            ('club_faculty', 'My Club Faculty Advisor'),
        ]
        context['coordinated_clubs'] = list(coordinator_clubs.values('id', 'name'))
        
    elif 'CLUB_ADVISOR' in user_roles:
        # Club advisor can send to their advised club members
        advised_clubs = user.advised_clubs.all()
        context['recipient_options'] = [
            ('club_members', 'Advised Club Members'),
            ('all_advisees', 'All Members from Advised Clubs'),
        ]
        context['advised_clubs'] = list(advised_clubs.values('id', 'name'))
        
    elif 'DEPARTMENT_ADMIN' in user_roles or 'DEPARTMENT_VP' in user_roles or 'EVENT_ORGANIZER' in user_roles:
        # Department admin/VP/EO can send to their department students
        user_department = user.department
        context['recipient_options'] = [
            ('dept_students', 'Department Students'),
            ('dept_faculty', 'Department Faculty'),
            ('all_students', 'All Students'),
        ]
        if user_department:
            context['user_department'] = {'id': user_department.id, 'name': user_department.name}
    
    elif 'PRESIDENT' in user_roles or 'SVP' in user_roles:
        # President/SVP can send to all students and specific groups
        context['recipient_options'] = [
            ('all_students', 'All Students'),
            ('all_users', 'All Users'),
            ('specific_club', 'Specific Club'),
            ('specific_department', 'Specific Department'),
        ]
    
    elif 'SECRETARY' in user_roles or 'TREASURER' in user_roles:
        # Secretary/Treasurer can send to all
        context['recipient_options'] = [
            ('all', 'All Users'),
            ('all_students', 'All Students'),
        ]
    
    # Get list of clubs and departments for dropdown
    context['clubs'] = list(Club.objects.all().values('id', 'name'))
    context['departments'] = list(Department.objects.all().values('id', 'name'))
    
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        recipient_type = request.POST.get('recipient_type', '')
        scope_value = request.POST.get('scope_value', '')  # For specific club/department
        
        if not message_text:
            messages.error(request, 'Message cannot be empty.')
            return render(request, 'notifications/send_notification.html', context)
        
        if len(message_text) > 500:
            messages.error(request, 'Message cannot exceed 500 characters.')
            return render(request, 'notifications/send_notification.html', context)
        
        # Determine recipient users based on role and selection
        recipient_users = set()
        
        try:
            if 'ADMIN' in user_roles or 'SAC_COORDINATOR' in user_roles:
                # Admin/SAC notification logic
                if recipient_type == 'all':
                    recipient_users = set(User.objects.all())
                elif recipient_type == 'all_students':
                    all_users = User.objects.all()
                    recipient_users = {u for u in all_users if 'STUDENT' in (u.roles or [])}
                elif recipient_type == 'all_faculty':
                    all_users = User.objects.all()
                    recipient_users = {u for u in all_users if 'FACULTY' in (u.roles or [])}
                elif recipient_type == 'all_coordinators':
                    all_users = User.objects.all()
                    recipient_users = {u for u in all_users if 'CLUB_COORDINATOR' in (u.roles or [])}
                elif recipient_type == 'all_advisors':
                    all_users = User.objects.all()
                    recipient_users = {u for u in all_users if 'CLUB_ADVISOR' in (u.roles or [])}
                elif recipient_type == 'specific_club' and scope_value:
                    club = Club.objects.get(id=int(scope_value))
                    recipient_users = set(club.members.all())
                elif recipient_type == 'specific_department' and scope_value:
                    dept = Department.objects.get(id=int(scope_value))
                    recipient_users = set(dept.users.all())
                    
            elif 'CLUB_COORDINATOR' in user_roles:
                # Club coordinator notification logic
                if recipient_type == 'club_members':
                    # Send to all members of coordinated clubs
                    coordinator_clubs = user.coordinated_clubs.all()
                    for club in coordinator_clubs:
                        recipient_users.update(club.members.all())
                elif recipient_type == 'club_faculty':
                    # Send to faculty advisors of coordinated clubs
                    coordinator_clubs = user.coordinated_clubs.all()
                    for club in coordinator_clubs:
                        if club.advisor:
                            recipient_users.add(club.advisor)
                            
            elif 'CLUB_ADVISOR' in user_roles:
                # Club advisor notification logic
                advised_clubs = user.advised_clubs.all()
                if recipient_type == 'club_members':
                    for club in advised_clubs:
                        recipient_users.update(club.members.all())
                elif recipient_type == 'all_advisees':
                    for club in advised_clubs:
                        recipient_users.update(club.members.all())
                        
            elif 'DEPARTMENT_ADMIN' in user_roles or 'DEPARTMENT_VP' in user_roles or 'EVENT_ORGANIZER' in user_roles:
                # Department admin/VP/EO notification logic
                user_dept = user.department
                if recipient_type == 'dept_students' and user_dept:
                    all_users = User.objects.all()
                    recipient_users = {u for u in all_users 
                                     if u.department == user_dept and 'STUDENT' in (u.roles or [])}
                elif recipient_type == 'dept_faculty' and user_dept:
                    all_users = User.objects.all()
                    recipient_users = {u for u in all_users 
                                     if u.department == user_dept and 'FACULTY' in (u.roles or [])}
                elif recipient_type == 'all_students':
                    all_users = User.objects.all()
                    recipient_users = {u for u in all_users if 'STUDENT' in (u.roles or [])}
                    
            elif 'PRESIDENT' in user_roles or 'SVP' in user_roles:
                # President/SVP notification logic
                if recipient_type == 'all_students':
                    all_users = User.objects.all()
                    recipient_users = {u for u in all_users if 'STUDENT' in (u.roles or [])}
                elif recipient_type == 'all_users':
                    recipient_users = set(User.objects.all())
                elif recipient_type == 'specific_club' and scope_value:
                    club = Club.objects.get(id=int(scope_value))
                    recipient_users = set(club.members.all())
                elif recipient_type == 'specific_department' and scope_value:
                    dept = Department.objects.get(id=int(scope_value))
                    recipient_users = set(dept.users.all())
                    
            elif 'SECRETARY' in user_roles or 'TREASURER' in user_roles:
                # Secretary/Treasurer notification logic
                if recipient_type == 'all':
                    recipient_users = set(User.objects.all())
                elif recipient_type == 'all_students':
                    all_users = User.objects.all()
                    recipient_users = {u for u in all_users if 'STUDENT' in (u.roles or [])}
            
            # Create notifications for all recipient users
            if recipient_users:
                created_count = 0
                for recipient in recipient_users:
                    notification = Notification.objects.create(
                        user=recipient,
                        message=message_text
                    )
                    created_count += 1
                
                messages.success(request, f'Notification sent to {created_count} user(s).')
                return redirect('notifications_list')
            else:
                messages.warning(request, 'No users matched your criteria.')
                return render(request, 'notifications/send_notification.html', context)
                
        except (Club.DoesNotExist, Department.DoesNotExist, ValueError) as e:
            messages.error(request, f'Invalid selection: {str(e)}')
            return render(request, 'notifications/send_notification.html', context)
        except Exception as e:
            messages.error(request, f'Error sending notification: {str(e)}')
            return render(request, 'notifications/send_notification.html', context)
    
    return render(request, 'notifications/send_notification.html', context)
