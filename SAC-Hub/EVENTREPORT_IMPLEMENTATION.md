# EventReport Model Implementation Summary

## Overview
A comprehensive EventReport model has been created to manage event reports submitted by Club Coordinators and Club Advisors, with approval workflow by Admins and SAC Coordinators.

---

## Files Modified

### 1. `events/models.py`
**Added**: `EventReport` class
- Complete event reporting system with approval workflow
- Automatic notification system
- Budget tracking
- Event metrics tracking

### 2. `events/admin.py`
**Added**:
- `EventReportAdmin` class for Django admin interface
- Admin configurations for EventReport, EventAssociation, EventCollaboration, EventRegistration
- Custom fieldsets for better UI organization

### 3. `events/serializers.py`
**Added**: `EventReportSerializer` class
- REST API serialization for EventReport
- Includes nested user information (submitted_by_name, approved_by_name)
- Full field coverage for API endpoints

### 4. `events/views.py`
**Added**: `EventReportViewSet` class
- REST API ViewSet with permission-based filtering
- Role-based queryset filtering:
  - Club Coordinators: See their club's reports
  - Club Advisors: See their club's reports
  - Department Admins: See department events' reports
  - SAC Coordinators: See all reports
  - Other users: See only their own reports

### 5. `events/api_urls.py`
**Added**: EventReportViewSet registration in router

### 6. `events/migrations/0011_eventreport.py`
**Created**: Migration file for EventReport model

---

## EventReport Model Structure

### Fields
```
Basic Information:
- event (ForeignKey) → Event
- title (CharField, 200)
- description (TextField)

Submission:
- submitted_by (ForeignKey) → User
- status (CharField) → DRAFT, PENDING, APPROVED, REJECTED

Metrics:
- total_attendees (PositiveIntegerField)
- expected_attendees (PositiveIntegerField)
- budget_allocated (DecimalField)
- budget_used (DecimalField)

Analysis:
- highlights (TextField)
- challenges (TextField)
- lessons_learned (TextField)

Files:
- file (FileField) → upload_to='event_reports/'

Approval:
- approved_by (ForeignKey) → User
- approval_notes (TextField)

Timestamps:
- created_at (DateTimeField, auto_now_add)
- updated_at (DateTimeField, auto_now)
- submitted_at (DateTimeField, nullable)
- approved_at (DateTimeField, nullable)
```

---

## Workflow

### 1. Report Creation
- **Who**: Club Coordinator or Club Advisor
- **Action**: Create report with status='DRAFT'
- **Data**: Title, description, event metrics, analysis

### 2. Report Submission
- **Who**: Report creator
- **Action**: Change status from DRAFT → PENDING
- **Auto**: submitted_at timestamp set
- **Notification**: Admins and SAC Coordinators notified

### 3. Report Approval
- **Who**: Admin or SAC Coordinator
- **Action**: Review and set status to APPROVED or REJECTED
- **Fields**: approved_by, approval_notes, approved_at
- **Notification**: Report creator notified of decision

---

## API Endpoints

### REST API
```
GET    /api/event-reports/              # List all (filtered by role)
GET    /api/event-reports/{id}/         # Retrieve specific report
POST   /api/event-reports/              # Create new report
PUT    /api/event-reports/{id}/         # Update report
PATCH  /api/event-reports/{id}/         # Partial update
DELETE /api/event-reports/{id}/         # Delete report
```

### Django Admin
```
/admin/events/eventreport/  # Full CRUD interface
```

---

## Permission System

### Who Can Submit Reports
- ✅ Club Coordinators (CLUB_COORDINATOR)
- ✅ Club Advisors (CLUB_ADVISOR)

### Who Can Approve Reports
- ✅ Admins (ADMIN)
- ✅ SAC Coordinators (SAC_COORDINATOR)

### Query Filtering
```python
# Club Coordinators: Own club's events only
EventReport.objects.filter(event__club__in=user.coordinated_clubs.all())

# Club Advisors: Own club's events only
EventReport.objects.filter(event__club__in=user.advised_clubs.all())

# Department Admins: Own department's events only
EventReport.objects.filter(event__department=user.department)

# SAC Coordinators: All reports
EventReport.objects.all()
```

---

## Notifications

### Automatic Notifications Sent

1. **On Report Submission (DRAFT → PENDING)**
   - Recipient: All Admins and SAC Coordinators
   - Message: "New event report '{title}' for event '{event_name}' is pending approval."

2. **On Report Approval/Rejection**
   - Recipient: Report submitter
   - Message: "Your event report '{title}' has been {approved/rejected}."

---

## Usage Examples

### Create a Draft Report
```python
from events.models import EventReport, Event
from users.models import User

report = EventReport.objects.create(
    event=Event.objects.get(id=1),
    title="Event Report 2024",
    description="Detailed event description...",
    submitted_by=User.objects.get(username='coordinator1'),
    status='DRAFT'
)
```

### Submit Report for Approval
```python
from django.utils import timezone

report.status = 'PENDING'
report.submitted_at = timezone.now()
report.save()
# Notification automatically sent to admins
```

### Approve Report
```python
report.status = 'APPROVED'
report.approved_by = User.objects.get(username='admin1')
report.approved_at = timezone.now()
report.approval_notes = "Excellent report!"
report.save()
# Notification automatically sent to submitter
```

---

## Integration with Existing Models

### Links to Event Model
- Each report is tied to exactly one Event
- Deleting event cascades delete to reports

### Links to User Model
- `submitted_by`: Tracks who submitted
- `approved_by`: Tracks who approved
- Multiple user relationships supported

---

## Admin Interface Features

### List View
- Displays: title, event, status, submitted_by, created_at
- Search: title, event name
- Filters: status, creation date
- Sort: by creation date (newest first)

### Detail View
- Organized fieldsets:
  - Report Details
  - Event Metrics
  - Event Analysis
  - Approval
  - Timestamps (collapsible)
- Read-only: timestamps

---

## Database Migration

### Migration File
- Location: `events/migrations/0011_eventreport.py`
- Table name: `events_eventreport`
- Indexed fields: status (for faster queries)

### To Apply Migration
```bash
python manage.py migrate events
```

---

## Related Documentation
- See `EVENT_REPORT_MODEL.md` for detailed model documentation
- See Events Management page for UI integration
