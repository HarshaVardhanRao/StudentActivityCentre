# EventReport Model Documentation

## Overview
The `EventReport` model is designed to manage event reports submitted by Club Coordinators and Club Advisors, which can be approved by Admins or SAC Coordinators.

## Model Location
- **File**: `events/models.py`
- **Import**: `from events.models import EventReport`

## Model Fields

### Basic Information
- **event** (ForeignKey to Event): The event this report is for
- **title** (CharField, max_length=200): Event report title
- **description** (TextField): Detailed description of the event and outcomes

### Submission Details
- **submitted_by** (ForeignKey to User): Club Coordinator or Club Advisor who submitted the report
- **status** (CharField): One of 'DRAFT', 'PENDING', 'APPROVED', 'REJECTED'
  - DRAFT: Report is being prepared
  - PENDING: Report submitted for approval
  - APPROVED: Report has been approved
  - REJECTED: Report has been rejected

### Event Metrics
- **total_attendees** (PositiveIntegerField): Total number of attendees
- **expected_attendees** (PositiveIntegerField): Expected number of attendees
- **budget_used** (DecimalField): Budget amount used
- **budget_allocated** (DecimalField): Budget amount allocated

### Analysis
- **highlights** (TextField): Key highlights and achievements
- **challenges** (TextField): Challenges faced during the event
- **lessons_learned** (TextField): Lessons learned and recommendations for future events

### Files
- **file** (FileField): Attached report document or images (optional)

### Approval Process
- **approved_by** (ForeignKey to User): Admin or SAC Coordinator who approved the report
- **approval_notes** (TextField): Notes from approver

### Timestamps
- **created_at** (DateTimeField): When report was created
- **updated_at** (DateTimeField): When report was last updated
- **submitted_at** (DateTimeField): When report was submitted for approval
- **approved_at** (DateTimeField): When report was approved/rejected

## Permissions

### Who Can Create/Edit Reports
- Club Coordinators (CLUB_COORDINATOR role)
- Club Advisors (CLUB_ADVISOR role)

### Who Can Approve Reports
- Admins (ADMIN role)
- SAC Coordinators (SAC_COORDINATOR role)

## Related Models
- **Event**: The event the report belongs to
- **User**: Submitter and approver

## Available Endpoints

### API Endpoints (REST)
- `GET /api/event-reports/` - List all reports (filtered by user role)
- `GET /api/event-reports/{id}/` - Get specific report
- `POST /api/event-reports/` - Create new report
- `PUT /api/event-reports/{id}/` - Update report
- `DELETE /api/event-reports/{id}/` - Delete report

### Admin Interface
- `/admin/events/eventreport/` - Manage reports in Django Admin

## Usage Example

### Creating a Report
```python
from events.models import EventReport, Event
from users.models import User

event = Event.objects.get(id=1)
submitter = User.objects.get(username='coordinator1')

report = EventReport.objects.create(
    event=event,
    title="Annual Event Report",
    description="Detailed description of the event...",
    submitted_by=submitter,
    status='DRAFT',
    total_attendees=150,
    expected_attendees=200,
    budget_allocated=5000.00,
    budget_used=4800.00,
    highlights="Successfully achieved all goals...",
    challenges="Limited venue space...",
    lessons_learned="Need better marketing..."
)
```

### Submitting Report for Approval
```python
from django.utils import timezone

report.status = 'PENDING'
report.submitted_at = timezone.now()
report.save()
```

### Approving a Report
```python
from django.utils import timezone

admin_user = User.objects.get(username='admin1')

report.status = 'APPROVED'
report.approved_by = admin_user
report.approved_at = timezone.now()
report.approval_notes = "Great event! Well documented."
report.save()
```

## Workflow

1. **Draft**: Club Coordinator/Advisor creates report
2. **Pending**: Report submitted for approval
3. **Approved/Rejected**: Admin/SAC Coordinator reviews and approves/rejects

## Notifications
The model automatically sends notifications:
- When a report is submitted for approval (notifies admins/SAC coordinators)
- When a report is approved/rejected (notifies the submitter)

## Related Views
- Event Management page: Shows pending reports
- Reports dashboard: Display and manage reports
- Admin dashboard: Approve/reject reports

## Database Table
- Table name: `events_eventreport`
- Status index: Yes (for faster queries)
- Ordering: By creation date (newest first)
