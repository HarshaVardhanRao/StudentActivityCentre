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