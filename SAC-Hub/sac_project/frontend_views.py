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
from django.http import JsonResponse
from django.views.decorators.http import require_POST

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
    
    # Show important notifications first
    notifications = notifications.order_by('-important', '-created_at')
    
    # Get counts
    total_count = user.notifications.count()
    unread_count = user.notifications.filter(read=False).count()
    read_count = user.notifications.filter(read=True).count()
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    # Determine non-student roles: if a user has STUDENT plus another role,
    # treat them as the other role for permission checks and UI.
    raw_roles = user.roles if isinstance(user.roles, list) else []
    user_roles = [r for r in raw_roles if r != 'STUDENT'] or raw_roles
    allowed_roles = ['ADMIN', 'SAC_COORDINATOR', 'CLUB_COORDINATOR', 'CLUB_ADVISOR', 
                     'DEPARTMENT_ADMIN', 'DEPARTMENT_VP', 'EVENT_ORGANIZER', 
                     'PRESIDENT', 'SVP', 'SECRETARY', 'TREASURER']
    can_send = any(role in user_roles for role in allowed_roles)

    context = {
        'notifications': notifications,
        'filter': filter_type,
        'total_count': total_count,
        'unread_count': unread_count,
        'read_count': read_count,
        'can_send_notifications': can_send,
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
    # Prefer non-student role if present (e.g., ['STUDENT','CLUB_COORDINATOR'])
    raw_roles = user.roles if isinstance(user.roles, list) else []
    user_roles = [r for r in raw_roles if r != 'STUDENT'] or raw_roles
    
    # Check if user has permission to send notifications. Treat users who are
    # students but have an additional role as that additional role.
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
        # Expose only the coordinator's clubs for selection (allow multi-select client-side)
        context['coordinated_clubs'] = list(coordinator_clubs.values('id', 'name'))
        context['allow_multi_club_select'] = True
        
    elif 'CLUB_ADVISOR' in user_roles:
        # Club advisor can send to their advised club members
        advised_clubs = user.advised_clubs.all()
        context['recipient_options'] = [
            ('club_members', 'Advised Club Members'),
            ('all_advisees', 'All Members from Advised Clubs'),
        ]
        context['advised_clubs'] = list(advised_clubs.values('id', 'name'))
        context['allow_multi_club_select'] = True
        
    elif 'DEPARTMENT_ADMIN' in user_roles or 'DEPARTMENT_VP' in user_roles or 'EVENT_ORGANIZER' in user_roles:
        # Department admin/VP/EO can send to their department students
        user_department = user.department
        context['recipient_options'] = [
            ('dept_students', 'Department Students'),
            ('dept_faculty', 'Department Faculty'),
            # Dept roles are restricted to their own department; do not expose 'all_students' here
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
        context['allow_multi_club_select'] = True
        context['allow_multi_dept_select'] = True
    
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
        # Support multi-select fields named 'clubs' and 'departments'
        scope_value = request.POST.get('scope_value', '')  # legacy single selection
        selected_club_ids = request.POST.getlist('clubs') or ([] if not scope_value else [scope_value])
        selected_dept_ids = request.POST.getlist('departments') or ([] if not scope_value else [scope_value])
        
        if not message_text:
            messages.error(request, 'Message cannot be empty.')
            return render(request, 'notifications/send_notification.html', context)
        
        if len(message_text) > 500:
            messages.error(request, 'Message cannot exceed 500 characters.')
            return render(request, 'notifications/send_notification.html', context)
        
        # Determine recipient users based on role and selection (use querysets)
        recipient_qs = User.objects.none()
        
        try:
            if 'ADMIN' in user_roles or 'SAC_COORDINATOR' in user_roles:
                # Admin/SAC notification logic (allow multi-select)
                if recipient_type == 'all':
                    recipient_qs = User.objects.all()
                elif recipient_type == 'all_students':
                    recipient_qs = User.objects.filter(roles__contains=['STUDENT'])
                elif recipient_type == 'all_faculty':
                    recipient_qs = User.objects.filter(roles__contains=['FACULTY'])
                elif recipient_type == 'all_coordinators':
                    recipient_qs = User.objects.filter(roles__contains=['CLUB_COORDINATOR'])
                elif recipient_type == 'all_advisors':
                    recipient_qs = User.objects.filter(roles__contains=['CLUB_ADVISOR'])
                elif recipient_type == 'specific_club' and selected_club_ids:
                    recipient_qs = User.objects.filter(clubs__id__in=selected_club_ids)
                elif recipient_type == 'specific_department' and selected_dept_ids:
                    recipient_qs = User.objects.filter(department__id__in=selected_dept_ids)
                    
            elif 'CLUB_COORDINATOR' in user_roles:
                # Club coordinator notification logic
                coordinator_club_ids = set(user.coordinated_clubs.values_list('id', flat=True))
                # If clubs were selected, ensure they are subset of coordinator's clubs
                if selected_club_ids:
                    requested = set(int(c) for c in selected_club_ids)
                    if not requested.issubset(coordinator_club_ids):
                        messages.error(request, 'You may only target your own coordinated club(s).')
                        return render(request, 'notifications/send_notification.html', context)
                    recipient_qs = User.objects.filter(clubs__id__in=requested)
                else:
                    # No selection — default to all members of coordinated clubs
                    recipient_qs = User.objects.filter(clubs__id__in=coordinator_club_ids)
                if recipient_type == 'club_faculty':
                    # advisors of the coordinator's clubs
                    recipient_qs = User.objects.filter(advised_clubs__id__in=coordinator_club_ids)
                            
            elif 'CLUB_ADVISOR' in user_roles:
                # Club advisor notification logic
                advised_club_ids = set(user.advised_clubs.values_list('id', flat=True))
                if selected_club_ids:
                    requested = set(int(c) for c in selected_club_ids)
                    if not requested.issubset(advised_club_ids):
                        messages.error(request, 'You may only target your advised club(s).')
                        return render(request, 'notifications/send_notification.html', context)
                    recipient_qs = User.objects.filter(clubs__id__in=requested)
                else:
                    # default to all advised club members
                    recipient_qs = User.objects.filter(clubs__id__in=advised_club_ids)
                        
            elif 'DEPARTMENT_ADMIN' in user_roles or 'DEPARTMENT_VP' in user_roles or 'EVENT_ORGANIZER' in user_roles:
                # Department admin/VP/EO notification logic — restricted to own department
                user_dept = user.department
                if not user_dept:
                    messages.error(request, 'You are not assigned to a department.')
                    return render(request, 'notifications/send_notification.html', context)
                if recipient_type == 'dept_students' and user_dept:
                    recipient_qs = User.objects.filter(department=user_dept, roles__contains=['STUDENT'])
                elif recipient_type == 'dept_faculty' and user_dept:
                    recipient_qs = User.objects.filter(department=user_dept, roles__contains=['FACULTY'])
                else:
                    messages.error(request, 'Invalid recipient selection for your role.')
                    return render(request, 'notifications/send_notification.html', context)
                    
            elif 'PRESIDENT' in user_roles or 'SVP' in user_roles:
                # President/SVP notification logic (allow multi-select)
                if recipient_type == 'all_students':
                    recipient_qs = User.objects.filter(roles__contains=['STUDENT'])
                elif recipient_type == 'all_users':
                    recipient_qs = User.objects.all()
                elif recipient_type == 'specific_club' and selected_club_ids:
                    recipient_qs = User.objects.filter(clubs__id__in=selected_club_ids)
                elif recipient_type == 'specific_department' and selected_dept_ids:
                    recipient_qs = User.objects.filter(department__id__in=selected_dept_ids)
                    
            elif 'SECRETARY' in user_roles or 'TREASURER' in user_roles:
                # Secretary/Treasurer notification logic
                if recipient_type == 'all':
                    recipient_qs = User.objects.all()
                elif recipient_type == 'all_students':
                    recipient_qs = User.objects.filter(roles__contains=['STUDENT'])
            
            # Create notifications for all recipient users (queryset)
            recipient_qs = recipient_qs.distinct()
            total = recipient_qs.count()
            if total > 0:
                created_count = 0
                for recipient in recipient_qs:
                    Notification.objects.create(user=recipient, message=message_text, important=bool(request.POST.get('important')))
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


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    from users.models import Notification
    try:
        n = Notification.objects.get(id=notification_id)
        # Only allow owner or admins to modify
        if n.user != request.user and 'ADMIN' not in (request.user.roles or []):
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        n.read = True
        n.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)


@login_required
@require_POST
def mark_notification_unread(request, notification_id):
    from users.models import Notification
    try:
        n = Notification.objects.get(id=notification_id)
        if n.user != request.user and 'ADMIN' not in (request.user.roles or []):
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        n.read = False
        n.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)


@login_required
@require_POST
def delete_notification(request, notification_id):
    from users.models import Notification
    try:
        n = Notification.objects.get(id=notification_id)
        if n.user != request.user and 'ADMIN' not in (request.user.roles or []):
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        n.delete()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Not found'}, status=404)


@login_required
@require_POST
def mark_all_read(request):
    from users.models import Notification
    # Admins can mark all users' notifications; otherwise only the user's
    if 'ADMIN' in (request.user.roles or []):
        Notification.objects.filter(read=False).update(read=True)
    else:
        Notification.objects.filter(user=request.user, read=False).update(read=True)
    return JsonResponse({'success': True})


@login_required
@require_POST
def clear_all_notifications(request):
    from users.models import Notification
    if 'ADMIN' in (request.user.roles or []):
        Notification.objects.all().delete()
    else:
        Notification.objects.filter(user=request.user).delete()
    return JsonResponse({'success': True})
