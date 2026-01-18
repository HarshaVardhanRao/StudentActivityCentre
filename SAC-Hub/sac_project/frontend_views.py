from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
import csv
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import calendar
import json
from django.utils import timezone

from events.models import Event
from events.models import EventRegistration
from attendance.models import Attendance, AttendanceSession
from calendar_app.models import CalendarEntry
from users.models import User, Club, Department
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def calendar_view(request):
    """Display calendar view with approved events - accessible to everyone"""
    # Get month and year from request
    month = int(request.GET.get('month', timezone.localtime(timezone.now()).month))
    year = int(request.GET.get('year', timezone.localtime(timezone.now()).year))
    
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
                is_today = day_date.date() == timezone.localtime(timezone.now()).date()
                
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

    # Permission: organizers, club coordinators, club advisor, or admin
    user_roles = request.user.roles if isinstance(request.user.roles, list) else []
    is_club_coordinator = request.user in (event.club.coordinators.all() if event.club else [])
    is_club_advisor = event.club and event.club.advisor == request.user
    is_organizer = request.user in event.organizers.all()
    if not (is_organizer or is_club_coordinator or is_club_advisor or 'ADMIN' in user_roles):
        messages.error(request, 'You do not have permission to manage attendance for this event.')
        return redirect('event_detail', event_id=event.id)

    # Determine session selection: prefer explicit session_id, else label
    session_id = request.GET.get('session_id')
    session_label = request.GET.get('session_label', '').strip()
    now = timezone.now()

    # Attendance sessions: allow selecting by id or label
    if session_id:
        try:
            session = event.attendance_sessions.get(id=session_id)
        except AttendanceSession.DoesNotExist:
            session = None
    else:
        session_qs = event.attendance_sessions.filter(label=session_label) if session_label else event.attendance_sessions
        session = session_qs.filter(locked=False).order_by('-created_at').first()

    # Calculate official open time (30 minutes before event start)
    open_time = event.date_time - timedelta(minutes=30)

    # If there's no active session, create one only if window has opened
    if not session:
        # Allow opening a session at any time. By default set the official open_at to
        # event_time - 30 minutes; allow `?force_open=1` to make it open immediately.
        if 'force_open' in request.GET:
            open_at_value = now
        else:
            open_at_value = open_time
        session = event.attendance_sessions.create(
            label=session_label,
            created_by=request.user,
            open_at=open_at_value
        )

    # Provide list of existing sessions for UI
    sessions = event.attendance_sessions.order_by('-created_at')

    # If session is locked, no further action
    if session.locked:
        messages.info(request, 'Attendance for this session has been submitted and is locked.')

    # Use EventRegistration to get eligible students (only REGISTERED)
    registered_qs = event.registrations.filter(status='REGISTERED').select_related('student')
    students = User.objects.filter(id__in=registered_qs.values_list('student_id', flat=True))

    # If session is locked, disallow modifications via POST
    if session.locked and request.method == 'POST':
        messages.error(request, 'This attendance session has been submitted and is locked.')
        return redirect('attendance_manage', event_id=event.id)

    # Handle POST actions: update attendance, register student (spot), submit/close, extend
    if request.method == 'POST':
        # Create a new session explicitly
        if request.POST.get('action') == 'new_session':
            label = request.POST.get('label', '').strip()
            force = request.POST.get('force_open') in ('1', 'true', 'on')
            open_at_value = now if force else open_time
            new_session = event.attendance_sessions.create(
                label=label,
                created_by=request.user,
                open_at=open_at_value
            )
            # Redirect to the attendance manage view with the created session selected
            url = reverse('attendance_manage', args=[event.id])
            return redirect(f"{url}?session_id={new_session.id}")

        # Submit final attendance
        if request.POST.get('action') == 'submit':
            # Only designated authorities can submit
            if not (is_organizer or is_club_coordinator or is_club_advisor or 'ADMIN' in user_roles):
                messages.error(request, 'Not authorized to submit attendance.')
                return redirect('attendance_manage', event_id=event.id)
            # Enforce submission constraints: session must be open (open_at <= now and not closed)
            if not session.is_open():
                messages.error(request, 'Attendance session is not open for submission yet or has been closed.')
                return redirect('attendance_manage', event_id=event.id)
            session.submitted_by = request.user
            session.submitted_at = now
            session.locked = True
            session.close_at = now
            session.save()
            messages.success(request, f'Attendance submitted. Code: {session.attendance_code}')
            return redirect('attendance_manage', event_id=event.id)

        # Extend session manually
        if request.POST.get('action') == 'extend':
            # Only club advisor, coordinator, event organizer allowed
            if not (is_organizer or is_club_coordinator or is_club_advisor or 'ADMIN' in user_roles):
                messages.error(request, 'Not authorized to extend attendance.')
                return redirect('attendance_manage', event_id=event.id)
            # Extend by minutes provided or default 10
            try:
                extra = int(request.POST.get('extend_minutes', '10'))
            except ValueError:
                extra = 10
            # set close_at to now + extra
            session.close_at = now + timedelta(minutes=extra)
            session.save()
            messages.success(request, f'Attendance extended by {extra} minutes.')
            return redirect('attendance_manage', event_id=event.id)

        # Spot registration: allow student to register before session close
        if request.POST.get('action') == 'spot_register':
            student_id = request.POST.get('student_id')
            try:
                student = User.objects.get(id=int(student_id))
            except Exception:
                messages.error(request, 'Invalid student selection.')
                return redirect('attendance_manage', event_id=event.id)
            # Only allow before session close
            if session.close_at and now > session.close_at:
                messages.error(request, 'Registration window closed for this attendance session.')
                return redirect('attendance_manage', event_id=event.id)
            # Create EventRegistration if not exists
            reg, created = EventRegistration.objects.get_or_create(event=event, student=student, defaults={'status': 'REGISTERED'})
            if created:
                messages.success(request, 'Student registered for the event.')
            else:
                messages.info(request, 'Student already registered.')
            return redirect('attendance_manage', event_id=event.id)

        # Handle attendance updates sent as JSON
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                for student_id, status in data.items():
                    student = User.objects.get(id=student_id)
                    # Only registered students allowed
                    if not event.registrations.filter(student=student, status='REGISTERED').exists():
                        continue
                    att, created = Attendance.objects.get_or_create(session=session, student=student, defaults={'status': status})
                    if not created:
                        att.status = status
                        att.save()
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})

    # Get existing attendance records for this session
    attendances = session.records.select_related('student').all()
    attendance_dict = {att.student_id: att for att in attendances}

    # Attach attendance object directly on student objects for easy template access
    # (templates can't index dicts by variable without a custom filter)
    if students is not None:
        # students may be a queryset; iterate and set attribute
        for student in students:
            setattr(student, 'attendance', attendance_dict.get(student.id))

    # Statistics
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
        'session': session,
        'sessions': sessions,
        'students': students,
        'attendance_dict': attendance_dict,
        'attendance_stats': attendance_stats,
    }
    return render(request, 'attendance/attendance_manage.html', context)


@login_required
def attendance_export(request, event_id):
    """Export attendance CSV for an event/session."""
    event = get_object_or_404(Event, id=event_id)
    # Permission as attendance_manage: organizers, club coordinators, club advisor, or admin
    user_roles = request.user.roles if isinstance(request.user.roles, list) else []
    is_club_coordinator = request.user in (event.club.coordinators.all() if event.club else [])
    is_club_advisor = event.club and event.club.advisor == request.user
    is_organizer = request.user in event.organizers.all()
    if not (is_organizer or is_club_coordinator or is_club_advisor or 'ADMIN' in user_roles):
        return HttpResponse('Not authorized', status=403)

    session_id = request.GET.get('session_id')
    session = None
    if session_id:
        try:
            session = event.attendance_sessions.get(id=session_id)
        except AttendanceSession.DoesNotExist:
            session = None

    if session:
        attendances = session.records.select_related('student').all()
        filename = f"attendance_event_{event.id}_session_{session.id}.csv"
    else:
        attendances = Attendance.objects.filter(session__event=event).select_related('student', 'session')
        filename = f"attendance_event_{event.id}.csv"

    # Build CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(['Roll Number', 'Full Name', 'Department', 'Status', 'Timestamp', 'Session', 'Reference'])
    for att in attendances:
        student = att.student
        roll = getattr(student, 'roll_no', '')
        # Call get_full_name() if it's a callable, otherwise fall back to first/last name
        full_name_attr = getattr(student, 'get_full_name', None)
        if callable(full_name_attr):
            full = full_name_attr()
        else:
            full = f"{student.first_name} {student.last_name}"
        dept = student.department.name if getattr(student, 'department', None) else ''
        status = att.status
        ts = att.timestamp.isoformat() if getattr(att, 'timestamp', None) else ''
        sess = att.session.label if getattr(att, 'session', None) and att.session.label else (getattr(att, 'session', None) and str(att.session.id) or '')
        ref = getattr(att, 'ref_code', '')
        writer.writerow([roll, full, dept, status, ts, sess, ref])

    return response


def attendance_verify(request):
    """Public-facing verification endpoint that accepts a reference code
    and shows the attended student's info. Accessible without authentication.
    If JSON is requested, returns JSON.
    """
    ref = (request.GET.get('ref') or request.POST.get('ref') or '').strip()
    result = None
    error = None
    if ref:
        # Case-insensitive, trimmed lookup to be tolerant of user input
        try:
            att = Attendance.objects.select_related('student', 'session__event').get(ref_code__iexact=ref)
            result = {
                'event': att.session.event.name if att.session and att.session.event else None,
                'session_label': att.session.label if att.session else None,
                'student_roll': getattr(att.student, 'roll_no', None),
                'student_name': att.student.get_full_name() if callable(getattr(att.student, 'get_full_name', None)) else f"{att.student.first_name} {att.student.last_name}",
                'status': att.status,
                'timestamp': att.timestamp.isoformat() if att.timestamp else None,
                'ref': att.ref_code,
            }
        except Attendance.DoesNotExist:
            error = 'Reference not found'

    # If client asked for JSON (Accept header) or requested format=json, return JSON
    if request.GET.get('format') == 'json' or request.headers.get('Accept', '').startswith('application/json'):
        if result:
            return JsonResponse({'success': True, 'attendance': result})
        return JsonResponse({'success': False, 'error': error or 'No ref provided'}, status=404)

    return render(request, 'attendance/verify.html', {'result': result, 'error': error, 'ref': ref})

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
        if attendance.session and attendance.session.event:
            recent_activities.append({
                'event': attendance.session.event,
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


@login_required
def attendance_list(request):
    """List attendance sessions for club coordinator's events"""
    from users.models import Club
    from django.db.models import Count, Q
    
    # Check if user is a club coordinator
    coordinator_clubs = Club.objects.filter(coordinators=request.user)
    if not coordinator_clubs.exists() and 'ADMIN' not in (request.user.roles or []):
        messages.error(request, 'You do not have permission to view attendance sessions.')
        return redirect('home')
    
    # Get all events from coordinator's clubs
    if 'ADMIN' in (request.user.roles or []):
        events = Event.objects.all().prefetch_related('attendance_sessions', 'club')
    else:
        events = Event.objects.filter(club__in=coordinator_clubs).prefetch_related('attendance_sessions', 'club')
    
    # Add session counts to events
    events_with_counts = []
    for event in events:
        sessions = event.attendance_sessions.all()
        open_sessions = sessions.filter(locked=False).count()
        submitted_sessions = sessions.filter(locked=True).count()
        events_with_counts.append({
            'event': event,
            'open_sessions_count': open_sessions,
            'submitted_sessions_count': submitted_sessions
        })
    
    # Get recent sessions across all events
    recent_sessions = AttendanceSession.objects.filter(
        event__club__in=coordinator_clubs if not 'ADMIN' in (request.user.roles or []) else Q()
    ).order_by('-created_at')[:10]
    
    # Calculate statistics
    total_events = len(events_with_counts)
    all_sessions = AttendanceSession.objects.filter(
        event__club__in=coordinator_clubs if not 'ADMIN' in (request.user.roles or []) else Q()
    )
    open_sessions_count = all_sessions.filter(locked=False).count()
    submitted_sessions_count = all_sessions.filter(locked=True).count()
    total_records = Attendance.objects.filter(
        session__event__club__in=coordinator_clubs if not 'ADMIN' in (request.user.roles or []) else Q()
    ).count()
    
    context = {
        'coordinator_clubs': coordinator_clubs,
        'events': [item['event'] for item in events_with_counts],
        'events_data': events_with_counts,
        'recent_sessions': recent_sessions,
        'total_events': total_events,
        'open_sessions': open_sessions_count,
        'submitted_sessions': submitted_sessions_count,
        'total_records': total_records,
    }
    
    return render(request, 'attendance/attendance_list.html', context)


@login_required
def attendance_report(request, event_id):
    """Display attendance report for a specific event"""
    event = get_object_or_404(Event, id=event_id)
    
    # Permission check: coordinator, advisor, organizer, or admin
    user_roles = request.user.roles if isinstance(request.user.roles, list) else []
    is_club_coordinator = request.user in (event.club.coordinators.all() if event.club else [])
    is_club_advisor = event.club and event.club.advisor == request.user
    is_organizer = request.user in event.organizers.all()
    
    if not (is_organizer or is_club_coordinator or is_club_advisor or 'ADMIN' in user_roles):
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('attendance_list')
    
    # Get all sessions for this event
    sessions = event.attendance_sessions.all().prefetch_related('records__student')
    
    # Add statistics to each session
    for session in sessions:
        records = session.records.all()
        present_count = records.filter(status='PRESENT').count()
        absent_count = records.filter(status='ABSENT').count()
        total_count = records.count()
        percentage = (present_count / total_count * 100) if total_count > 0 else 0
        
        session.present_count = present_count
        session.absent_count = absent_count
        session.total_count = total_count
        session.percentage = percentage
    
    # Overall statistics
    all_records = Attendance.objects.filter(session__event=event)
    overall_stats = {
        'total_present': all_records.filter(status='PRESENT').count(),
        'total_absent': all_records.filter(status='ABSENT').count(),
        'total_records': all_records.count(),
    }
    
    submitted_sessions_count = sessions.filter(locked=True).count()
    open_sessions_count = sessions.filter(locked=False).count()
    
    context = {
        'event': event,
        'sessions': sessions,
        'overall_stats': overall_stats,
        'submitted_sessions_count': submitted_sessions_count,
        'open_sessions_count': open_sessions_count,
    }
    
    return render(request, 'attendance/attendance_report.html', context)


@login_required
def analytics_view(request):
    """Analytics dashboard for SAC_COORDINATOR only"""
    # Role-based access control
    user_roles = request.user.roles if isinstance(request.user.roles, list) else []
    if 'SAC_COORDINATOR' not in user_roles and 'ADMIN' not in user_roles:
        messages.error(request, 'You do not have permission to access analytics.')
        return redirect('student-dashboard')
    
    from django.db.models import Count, Q, Avg, F
    from django.utils import timezone
    from datetime import timedelta
    
    # Get current date for filtering
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # === CLUB STATISTICS ===
    total_clubs = Club.objects.count()
    active_clubs = Club.objects.filter(members__isnull=False).distinct().count()
    
    # Get top clubs by members
    top_clubs = Club.objects.annotate(member_count=Count('members')).order_by('-member_count')[:5]
    
    # === DEPARTMENT STATISTICS ===
    total_departments = Department.objects.count()
    departments_with_data = Department.objects.annotate(
        student_count=Count('users', filter=Q(users__roles__contains=['STUDENT']))
    ).order_by('-student_count')
    
    # === EVENT STATISTICS ===
    total_events = Event.objects.count()
    approved_events = Event.objects.filter(status='APPROVED').count()
    pending_events = Event.objects.filter(status='PENDING').count()
    draft_events = Event.objects.filter(status='DRAFT').count()
    rejected_events = Event.objects.filter(status='REJECTED').count()
    
    # Events in last 30 days
    recent_events = Event.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Events by club
    events_by_club = Club.objects.annotate(event_count=Count('events')).filter(event_count__gt=0).order_by('-event_count')[:5]
    
    # === ATTENDANCE STATISTICS ===
    total_attendance_records = Attendance.objects.count()
    present_count = Attendance.objects.filter(status='PRESENT').count()
    absent_count = Attendance.objects.filter(status='ABSENT').count()
    
    # Calculate overall attendance percentage
    overall_attendance_percentage = (present_count / total_attendance_records * 100) if total_attendance_records > 0 else 0
    
    # Attendance by department
    attendance_by_dept = Department.objects.annotate(
        total_attendance=Count('users__attendances'),
        present_attendance=Count('users__attendances', filter=Q(users__attendances__status='PRESENT'))
    ).values('id', 'name', 'total_attendance', 'present_attendance').order_by('-total_attendance')
    
    # Calculate percentage for each department
    dept_attendance_data = []
    for dept in attendance_by_dept:
        if dept['total_attendance'] > 0:
            percentage = (dept['present_attendance'] / dept['total_attendance'] * 100)
            dept_attendance_data.append({
                'name': dept['name'],
                'total': dept['total_attendance'],
                'present': dept['present_attendance'],
                'percentage': round(percentage, 2)
            })
    
    # === PARTICIPATION STATISTICS ===
    total_registrations = EventRegistration.objects.count()
    
    # Most attended events
    most_attended_events = Event.objects.annotate(
        attendance_count=Count('attendance_sessions__records', filter=Q(attendance_sessions__records__status='PRESENT'))
    ).filter(attendance_count__gt=0).order_by('-attendance_count')[:5]
    
    # Event-wise participation
    event_participation = Event.objects.annotate(
        registration_count=Count('registrations'),
        attendance_count=Count('attendance_sessions__records', filter=Q(attendance_sessions__records__status='PRESENT'))
    ).filter(Q(registration_count__gt=0) | Q(attendance_count__gt=0)).order_by('-registration_count')[:10]
    
    # Per-event data
    event_data = []
    for event in event_participation:
        event_data.append({
            'name': event.name,
            'registrations': event.registration_count,
            'attendance': event.attendance_count,
            'status': event.status
        })
    
    # === STUDENT STATISTICS ===
    # SQLite doesn't support contains lookup on JSON fields, so we filter in Python
    all_users = User.objects.all()
    total_students = len([user for user in all_users if 'STUDENT' in (user.roles or [])])
    active_students = len([user for user in all_users if 'STUDENT' in (user.roles or []) and user.event_registrations.exists()])
    
    # Most active students (by registrations)
    student_registrations = {}
    for user in all_users:
        if 'STUDENT' in (user.roles or []):
            reg_count = user.event_registrations.count()
            att_count = user.attendances.count()
            if reg_count > 0 or att_count > 0:
                student_registrations[user.id] = {
                    'user': user,
                    'registration_count': reg_count,
                    'attendance_count': att_count,
                }
    
    # Sort by registration count and get top 5
    sorted_students = sorted(student_registrations.values(), key=lambda x: x['registration_count'], reverse=True)[:5]
    most_active_students = [item['user'] for item in sorted_students]
    # Attach counts as attributes for template access
    for i, student in enumerate(most_active_students):
        student.registration_count = sorted_students[i]['registration_count']
        student.attendance_count = sorted_students[i]['attendance_count']
    
    # === TIME-BASED STATISTICS ===
    # Events created in last 30 days by week
    events_last_30_days = Event.objects.filter(created_at__gte=thirty_days_ago).order_by('created_at')
    
    # Attendance in last 30 days
    recent_attendance = Attendance.objects.filter(timestamp__gte=thirty_days_ago)
    recent_present = recent_attendance.filter(status='PRESENT').count()
    recent_absent = recent_attendance.filter(status='ABSENT').count()
    recent_total = recent_attendance.count()
    
    # === CLUB PERFORMANCE ===
    club_performance = Club.objects.annotate(
        member_count=Count('members'),
        event_count=Count('events'),
        avg_attendance=Avg('events__attendance_sessions__records__status', filter=Q(events__attendance_sessions__records__status='PRESENT'))
    ).order_by('-event_count')[:5]
    
    # === CONTEXT DATA ===
    context = {
        # Club stats
        'total_clubs': total_clubs,
        'active_clubs': active_clubs,
        'top_clubs': top_clubs,
        
        # Department stats
        'total_departments': total_departments,
        'departments_with_data': departments_with_data,
        
        # Event stats
        'total_events': total_events,
        'approved_events': approved_events,
        'pending_events': pending_events,
        'draft_events': draft_events,
        'rejected_events': rejected_events,
        'recent_events': recent_events,
        'events_by_club': events_by_club,
        
        # Attendance stats
        'total_attendance_records': total_attendance_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'overall_attendance_percentage': round(overall_attendance_percentage, 2),
        'absent_percentage': round(100 - overall_attendance_percentage, 2),
        'dept_attendance_data': dept_attendance_data,
        
        # Participation stats
        'total_registrations': total_registrations,
        'most_attended_events': most_attended_events,
        'event_participation': event_data,
        
        # Student stats
        'total_students': total_students,
        'active_students': active_students,
        'most_active_students': most_active_students,
        
        # Time-based stats
        'recent_attendance_count': recent_total,
        'recent_present': recent_present,
        'recent_absent': recent_absent,
        'recent_attendance_percentage': (recent_present / recent_total * 100) if recent_total > 0 else 0,
        
        # Club performance
        'club_performance': club_performance,
    }
    
    return render(request, 'analytics/analytics_dashboard.html', context)
