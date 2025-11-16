# 🎓 Student Activity Centre Hub

A comprehensive Django-based web application for managing student activities, clubs, events, attendance, and organizational coordination.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Tech Stack](#tech-stack)
4. [System Architecture](#system-architecture)
5. [User Roles & Permissions](#user-roles--permissions)
6. [Admin Dashboard](#admin-dashboard)
7. [Installation & Setup](#installation--setup)
8. [Usage Guide](#usage-guide)
9. [API Reference](#api-reference)
10. [Database Models](#database-models)
11. [Testing](#testing)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

Student Activity Centre is a centralized platform that enables:
- **Club Management**: Create, manage, and organize student clubs
- **Event Coordination**: Plan events with approval workflows and notifications
- **Attendance Tracking**: Monitor student participation in events
- **Role-Based Access**: Multi-level permission system for different user types
- **Administrative Control**: Comprehensive admin dashboard for system management

**Current Version**: Production Ready  
**Status**: ✅ All systems operational

---

## ✨ Key Features

### 🔐 Role-Based Access Control
- **ADMIN**: Full system access and controls
- **SAC_COORDINATOR**: Event approval and oversight
- **CLUB_COORDINATOR**: Club management and event creation
- **CLUB_ADVISOR**: Advisor-specific operations
- **FACULTY**: Faculty-specific features
- **STUDENT**: Student participation and viewing
- **EVENT_ORGANIZER**: Event-specific management
- **DEPARTMENT_ADMIN**: Department-level management
- **TREASURER**: Financial tracking
- **SECRETARY**: Administrative support
- **STUDENT_VOLUNTEER**: Volunteer coordination
- **SVP**: Student Vice President functions

### 📊 Admin Dashboard
**Access**: `/dashboard/admin/` (ADMIN or SAC_COORDINATOR)

**Features**:
- Real-time statistics (8 key metrics)
- User Management (CRUD operations)
- Club Management (CRUD operations with interactive dropdowns)
- Department Management (CRUD operations)
- Event Management (view, edit, approval status)
- Attendance Tracking (view, edit, delete)
- Calendar Management (view, edit, delete)
- Notification System
- Permission-based access control
- Interactive dropdown menus for quick actions
- Modal dialogs for inline operations
- Responsive design for all devices

### 🎭 Club Management
- Create and manage clubs
- Assign coordinators and advisors
- Automatic role assignment (CLUB_COORDINATOR role)
- Member management
- Club-specific event creation

### 📅 Event Management
- **Event Creation**: Only authorized users (Faculty Advisors, Club Coordinators, Admins)
- **Optional Club Selection**: Club field is now optional for all users
  - Faculty/Coordinators can create standalone events
  - Only see applicable clubs in dropdown (clubs they advise/coordinate)
  - All clubs visible in associations/collaborations sections
- **Approval Workflow**: All events require admin approval
- **Status Tracking**: PENDING → APPROVED/REJECTED → COMPLETED
- **Notifications**: Auto-notifications for creation, approval, rejection
- **Attendance Integration**: Link events to attendance records

### 📋 Attendance System
- Student presence tracking
- Event-based attendance recording
- Status indicators (Present/Absent)
- Admin viewing and editing capabilities

### 📆 Calendar System
- Event calendar entries
- Visibility controls
- Entry type tracking
- Admin management interface

### 🔔 Notification System
- Automatic notifications for system events
- User-specific notification feeds
- Recent notifications display on dashboard

### 🎯 Automatic Role Assignment
**Club Coordinator Role**:
- Automatically added when user becomes club coordinator
- Maintained across multiple club assignments
- Automatically removed when user stops coordinating any club
- Handled via Django signals (no manual intervention needed)

---

## 🛠 Tech Stack

- **Backend**: Django 5.2.8 with Python 3.12
- **Database**: SQLite (development) / PostgreSQL (production-ready)
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Django's built-in auth system
- **API**: JSON-based REST endpoints
- **Styling**: Inline CSS with responsive design

---

## 🏗 System Architecture

### Project Structure
```
SAC-Hub/
├── sac_project/
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Main URL routing
│   ├── admin_views.py       # Admin CRUD operations
│   ├── role_dashboards.py   # Role-specific dashboards
│   ├── auth_views.py        # Authentication
│   └── ...
├── users/
│   ├── models.py            # User, Club, Department models
│   ├── signals.py           # Role assignment signals
│   ├── admin.py             # Django admin config
│   └── ...
├── events/
│   ├── models.py            # Event model
│   ├── views.py             # Event views
│   ├── frontend_views.py    # Frontend-specific views
│   └── ...
├── attendance/
│   ├── models.py            # Attendance tracking
│   └── ...
├── calendar_app/
│   ├── models.py            # Calendar entries
│   └── ...
├── templates/
│   ├── admin_dashboard.html # Main admin interface
│   ├── base.html            # Base template
│   └── ...
└── manage.py

db.sqlite3                     # Development database
```

### Data Flow
```
User Login → Dashboard Redirect → Role-Based View
    ↓
Admin → Admin Dashboard (stats, dropdowns, modals)
    ↓
Club Operations → Signal Handler → Role Update
    ↓
Event Creation → Approval Workflow → Notification
    ↓
Attendance/Calendar → Admin Management
```

---

## 👥 User Roles & Permissions

### Role Matrix

| Role | Dashboard | Create Events | Approve Events | Manage Users | Manage Clubs | Edit Attendance |
|------|-----------|---------------|----------------|--------------|--------------|-----------------|
| ADMIN | ✅ Full | ✅ Any | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| SAC_COORDINATOR | ✅ Full | ✅ Any | ✅ Yes | ⚠️ Limited | ⚠️ Limited | ✅ Yes |
| CLUB_COORDINATOR | ✅ Club | ✅ Own Clubs | ❌ No | ❌ No | ✅ Own Clubs | ❌ No |
| FACULTY | ✅ Faculty | ✅ Advised Clubs | ❌ No | ❌ No | ❌ No | ❌ No |
| CLUB_ADVISOR | ✅ Club | ✅ Advised Clubs | ❌ No | ❌ No | ❌ No | ❌ No |
| EVENT_ORGANIZER | ✅ Events | ✅ Limited | ❌ No | ❌ No | ❌ No | ✅ Events |
| STUDENT | ✅ Student | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No |

### Permission Rules

**Event Creation**:
- ✅ Faculty Advisors, Club Coordinators, Admins only
- ✅ Creates event in PENDING status
- ✅ Requires admin approval to activate

**Event Approval**:
- ✅ ADMIN and SAC_COORDINATOR roles only
- ✅ Change status to APPROVED/REJECTED/COMPLETED
- ✅ Add approval notes
- ✅ Send notifications

**Role Assignment**:
- ✅ ADMIN can assign any role
- ✅ Automatic CLUB_COORDINATOR role via signals
- ✅ Role cleanup when coordinator removed from all clubs

---

## 📊 Admin Dashboard

### Access
```
URL: http://localhost:8000/dashboard/admin/
Requirements: Login as ADMIN or SAC_COORDINATOR
```

### Dashboard Sections

#### 1. **Statistics Cards** (Real-time)
```
👥 Total Users          🎯 Total Clubs        🏢 Departments
📅 Events               ⏳ Pending Events      ✅ Approved Events
📋 Attendance Records   📆 Calendar Entries
```

#### 2. **Users Management**
```
Actions:
├── ➕ Add User          → Add new user via Django admin
├── 👁️ View All         → Full user list in admin
├── ⋯ Dropdown Menu
│   ├── ✏️ Edit          → Redirect to admin edit
│   ├── 👁️ View         → View user modal
│   └── 🗑️ Delete       → Confirm and delete
```

#### 3. **Clubs Management**
```
Actions:
├── ➕ Add Club          → Create new club via modal
├── 👁️ View All         → Full club list
├── ⋯ Dropdown Menu
│   ├── ✏️ Edit          → Edit club via modal
│   ├── 👁️ View         → View club details
│   └── 🗑️ Delete       → Confirm and delete
```

#### 4. **Departments Management**
```
Actions:
├── ➕ Add Department    → Create new department
├── 👁️ View All         → Full department list
├── ⋯ Dropdown Menu
│   ├── ✏️ Edit          → Edit department
│   ├── 👁️ View         → View details
│   └── 🗑️ Delete       → Confirm and delete
```

#### 5. **Events Management**
```
Actions:
├── ➕ Create Event      → Link to event creation
├── 👁️ View All         → Full event list
├── ⋯ Dropdown Menu
│   ├── 👁️ View         → Event details page
│   ├── ✏️ Edit          → Event edit page
│   └── 🗑️ Delete       → Confirmation dialog
```

#### 6. **Attendance Management**
```
Actions:
├── 👁️ View All         → Full attendance list
├── ⋯ Dropdown Menu
│   ├── ✏️ Edit          → Django admin edit
│   └── 🗑️ Delete       → Confirmation dialog
```

#### 7. **Calendar Management**
```
Actions:
├── 👁️ View All         → Full calendar list
├── ⋯ Dropdown Menu
│   ├── ✏️ Edit          → Django admin edit
│   └── 🗑️ Delete       → Confirmation dialog
```

#### 8. **Notifications**
```
Recent notifications (10 most recent)
Auto-updates on dashboard refresh
```

### Interactive Features

**Dropdown Menus**:
- Click "⋯ Actions" button on any row
- Select desired operation from dropdown
- Auto-closes when clicking outside

**Modal Dialogs**:
- For Club and Department create/edit
- Form validation before submission
- CSRF protection on API calls
- Real-time feedback with alerts

**Inline Operations**:
- Create/Edit/View/Delete without page navigation
- Page auto-refreshes after successful operation
- Confirmation dialogs for destructive actions

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.12+
- Django 5.2.8
- SQLite or PostgreSQL
- Virtual environment (recommended)

### Step 1: Clone Repository
```bash
git clone https://github.com/HarshaVardhanRao/StudentActivityCentre.git
cd StudentActivityCentre
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt  # If available
# Or install manually:
pip install django==5.2.8 psycopg2-binary python-decouple
```

### Step 4: Navigate to Project
```bash
cd SAC-Hub
```

### Step 5: Run Migrations
```bash
python manage.py migrate
```

### Step 6: Create Superuser
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

### Step 8: Access Application
- **Main App**: http://localhost:8000/
- **Admin Dashboard**: http://localhost:8000/dashboard/admin/
- **Django Admin**: http://localhost:8000/admin/

---

## 📖 Usage Guide

### Creating a Club

**Via Dashboard**:
1. Go to `/dashboard/admin/`
2. Click "➕ Add Club" in Clubs Management
3. Enter club name and description
4. Click "Save Club"
5. Dashboard refreshes with new club

**Via Django Admin**:
1. Go to `/admin/users/club/`
2. Click "Add Club"
3. Fill in all required fields
4. Select coordinators and advisor
5. Save

### Assigning Club Coordinators

**Automatic Role Assignment**:
1. Go to Clubs Management in dashboard
2. Edit a club
3. Select coordinators from available users
4. Save changes
5. System automatically:
   - Adds CLUB_COORDINATOR role to selected users
   - Maintains role across multiple club assignments
   - Removes role when user stops coordinating any club

### Creating Events

**Requirements**:
- Must have FACULTY, CLUB_ADVISOR, CLUB_COORDINATOR, or ADMIN role
- Faculty/Advisors can only create for their advised clubs
- Coordinators can only create for their clubs
- Admins can create for any club

**Process**:
1. Go to `/events/create/`
2. Select club (limited to user's clubs unless admin)
3. Fill in event details
4. Submit event (status: PENDING)
5. Wait for admin approval
6. Event goes live once approved

**Workflow**:
```
Event Created (PENDING)
    ↓ [Admin Review]
    → APPROVED (visible to users)
    → REJECTED (with feedback notes)
    ↓ [Event Occurs]
    → COMPLETED
```

### Approving Events

**Admin Only**:
1. Go to Dashboard → Admin section
2. View pending events in Events Management
3. Click event dropdown → View event
4. Provide approval decision and notes
5. Event status updates automatically
6. Notifications sent to event creator

### Managing Attendance

**Recording Attendance**:
1. Go to `/admin/attendance/attendance/`
2. Click "Add Attendance Record"
3. Select student and event
4. Mark status (Present/Absent)
5. Save

**Viewing Attendance**:
1. Dashboard → Attendance Management
2. Click "View All" for full list
3. Use dropdown to edit or delete records
4. Filter by event or student as needed

---

## 🔌 API Reference

### Admin CRUD Endpoints

#### Clubs API
```
Endpoint: POST /api/admin/clubs/
Permission: ADMIN or SAC_COORDINATOR

Create Club:
{
  "action": "create",
  "name": "Tech Club",
  "description": "For tech enthusiasts"
}

Update Club:
{
  "action": "update",
  "id": 1,
  "name": "Updated Name",
  "description": "Updated description"
}

Delete Club:
{
  "action": "delete",
  "id": 1
}

Response:
{
  "success": true,
  "message": "Operation successful",
  "club_id": 1
}
```

#### Departments API
```
Endpoint: POST /api/admin/departments/
Permission: ADMIN or SAC_COORDINATOR

Create Department:
{
  "action": "create",
  "name": "Computer Science",
  "description": "CS Department"
}

Update Department:
{
  "action": "update",
  "id": 1,
  "name": "Updated Name",
  "description": "Updated description"
}

Delete Department:
{
  "action": "delete",
  "id": 1
}

Response:
{
  "success": true,
  "message": "Operation successful",
  "dept_id": 1
}
```

#### Users API
```
Endpoint: POST /api/admin/users/
Permission: ADMIN or SAC_COORDINATOR

Get Users:
GET /api/admin/users/
Response:
{
  "success": true,
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "roles": ["STUDENT", "CLUB_COORDINATOR"]
    }
  ]
}

Update User Roles:
{
  "action": "update_roles",
  "id": 1,
  "roles": ["ADMIN", "FACULTY"]
}

Delete User:
{
  "action": "delete",
  "id": 1
}
```

### Authentication API

```
Login:
POST /login/
{
  "username": "admin",
  "password": "password"
}

Logout:
GET /logout/

Register:
POST /register/
{
  "username": "newuser",
  "email": "user@example.com",
  "password1": "password",
  "password2": "password"
}
```

### Event Approval API

```
Approve Event:
POST /admin/event-approvals/
{
  "event_id": 1,
  "action": "approve",
  "notes": "Approved - looks good"
}

Reject Event:
POST /admin/event-approvals/
{
  "event_id": 1,
  "action": "reject",
  "notes": "Please revise and resubmit"
}
```

---

## 🗄 Database Models

### Core Models

#### User (Custom AbstractUser)
```python
Fields:
- username (unique)
- email (unique)
- first_name, last_name
- roles (JSONField: list of role strings)
- department (ForeignKey)
- roll_no (optional)
- date_joined, last_login

Methods:
- get_full_name()
- is_admin(), is_coordinator(), etc.
```

#### Club
```python
Fields:
- name (unique)
- description
- coordinators (M2M to User)
- members (M2M to User)
- advisor (FK to User)
- created_at, updated_at

Methods:
- __str__()
- get_coordinator_count()
```

#### Department
```python
Fields:
- name (unique)
- description
- users (M2M to User)
- created_at

Methods:
- __str__()
```

#### Event
```python
Fields:
- name
- description
- date_time
- location
- club (FK to Club)
- created_by (FK to User)
- status (PENDING/APPROVED/REJECTED/COMPLETED)
- approval_notes
- created_at, updated_at

Methods:
- __str__()
- is_pending()
- is_approved()
```

#### Attendance
```python
Fields:
- event (FK to Event)
- student (FK to User)
- status (PRESENT/ABSENT)
- timestamp
- notes

Methods:
- __str__()
```

#### CalendarEntry
```python
Fields:
- event (FK to Event)
- date_time
- entry_type
- visible_to
- created_at

Methods:
- __str__()
```

#### Notification
```python
Fields:
- user (FK to User)
- message
- created_at
- is_read

Methods:
- __str__()
- mark_as_read()
```

---

## 🧪 Testing

### Running Tests

**All Tests**:
```bash
cd SAC-Hub
python manage.py test
```

**Specific App**:
```bash
python manage.py test users
python manage.py test events
python manage.py test attendance
```

**Specific Test File**:
```bash
python manage.py test users.tests.UserModelTest
```

### Test Files Included

1. **test_club_coordinator_role.py** - Basic coordinator role assignment
2. **test_comprehensive_coordinator_role.py** - Advanced role scenarios
3. **test_login.py** - Authentication tests
4. **test_secretary_role.py** - Secretary role functionality
5. **test_faculty_clubs.py** - Faculty club management

### Test Coverage

- ✅ User authentication
- ✅ Role-based access control
- ✅ Club coordinator role assignment
- ✅ Event creation and approval
- ✅ Attendance tracking
- ✅ Permission validation
- ✅ Signal handlers
- ✅ API endpoints

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Cannot import name 'dashboard_redirect'"
- **Solution**: Check `sac_project/role_dashboards.py` has `dashboard_redirect()` function
- **File**: `SAC-Hub/sac_project/role_dashboards.py`

**Issue**: Admin dashboard showing error or empty sections
- **Solution**: Ensure user has ADMIN or SAC_COORDINATOR role
- **Check**: User roles in `/admin/users/user/` or database
- **Fix**: Add role via: User.roles.append('ADMIN')

**Issue**: Club coordinator role not assigned
- **Solution**: Verify signals are registered
- **File**: `SAC-Hub/users/apps.py` should have `ready()` method
- **Check**: `SAC-Hub/users/signals.py` exists and has m2m_changed handler

**Issue**: Event creation button not visible
- **Solution**: User must have appropriate role
- **Required Roles**: FACULTY, CLUB_ADVISOR, CLUB_COORDINATOR, or ADMIN
- **Fix**: Assign role to user first

**Issue**: API endpoints return 403 Permission Denied
- **Solution**: User needs ADMIN or SAC_COORDINATOR role
- **Check**: `check_admin_permission()` in `admin_views.py`
- **Verify**: User roles and CSRF token

**Issue**: CSRF token errors on form submission
- **Solution**: Ensure form includes {% csrf_token %}
- **Check**: Template file has token in forms
- **Frontend**: JavaScript calls include CSRF token from cookies

**Issue**: Database migrations failing
- **Solution**: Run makemigrations first
```bash
python manage.py makemigrations
python manage.py migrate
```

**Issue**: Modal not opening or dropdown not showing
- **Solution**: Check browser console for JavaScript errors (F12)
- **Common Cause**: Missing CSRF token or jQuery
- **Fix**: Ensure all scripts are loaded correctly

### Debug Mode

**Enable Django Debug**:
```python
# settings.py
DEBUG = True
ALLOWED_HOSTS = ['*']
```

**Check Server Logs**:
```bash
# Terminal running Django server shows:
# - 200 (success)
# - 404 (not found)
# - 403 (permission denied)
# - 500 (server error)
```

**Database Queries**:
```python
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as context:
    # Your code here
    print(f"Total queries: {len(context)}")
```

---

## 📞 Support & Contact

- **Repository**: https://github.com/HarshaVardhanRao/StudentActivityCentre
- **Issues**: Use GitHub Issues for bug reports
- **Documentation**: Refer to inline code comments and docstrings

---

## 📄 License

This project is provided as-is for educational purposes.

---

## ✅ Project Status

- ✅ User authentication and roles
- ✅ Club management with coordinators
- ✅ Event creation and approval
- ✅ Attendance tracking
- ✅ Calendar management
- ✅ Admin dashboard with CRUD
- ✅ Interactive dropdown menus
- ✅ Modal dialogs for inline operations
- ✅ Permission-based access control
- ✅ Automatic role assignment via signals
- ✅ Responsive design (desktop/tablet/mobile)
- ✅ Notification system
- ✅ Comprehensive documentation
- ✅ Django checks passed (0 issues)
- ✅ All tests passing

**Ready for Production Deployment** 🚀

---

*Last Updated: November 16, 2025*  
*Maintained by: Development Team*