# My Registrations Page - Visual & Feature Guide

## Page Layout Overview

```
╔═════════════════════════════════════════════════════════════════════════╗
║                                                                         ║
║  SIDEBAR                    MAIN CONTENT AREA                          ║
║  ┌──────┐  ┌─────────────────────────────────────────────────────────┐ ║
║  │      │  │                                                         │ ║
║  │      │  │  My Event Registrations                                │ ║
║  │      │  │  Track and manage your event registrations             │ ║
║  │      │  │                              [Browse Events] →         │ ║
║  │      │  │                                                         │ ║
║  │      │  ├─────────────────────────────────────────────────────────┤ ║
║  │      │  │ [All] | [Registered] | [Participated]                 │ ║
║  │      │  ├─────────────────────────────────────────────────────────┤ ║
║  │      │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │ ║
║  │ HOME │  │  │ 12 Total   │  │ 10 Reg'd   │  │ 0 Certs    │        │ ║
║  │      │  │  │ Events     │  │ Events     │  │ Earned     │        │ ║
║  │ EVENTS   │  └────────────┘  └────────────┘  └────────────┘        │ ║
║  │      │  │                                                         │ ║
║  │ MY REG   │  Events Table                                          │ ║
║  │      │  │  ┌────────────────────────────────────────────────┐   │ ║
║  │ CERTS    │  │ EVENT  │ DATE  │ VENUE │ STATUS │ ACTIONS   │   │ ║
║  │      │  │  ├────────────────────────────────────────────────┤   │ ║
║  │      │  │  │🎨 Art  │Jan 18 │Main   │ ✓ Reg  │ [V][C]     │   │ ║
║  │      │  │  │Fest    │2PM    │Hall   │ Blue   │            │   │ ║
║  │ NOTIF    │  ├────────────────────────────────────────────────┤   │ ║
║  │      │  │  │🎵 Music│Jan 15 │Audio  │✓✓Part  │ [V]        │   │ ║
║  │      │  │  │Night   │6PM    │torium │ Green  │            │   │ ║
║  │      │  │  ├────────────────────────────────────────────────┤   │ ║
║  │ PROFILE  │  │ ...                                            │   │ ║
║  │      │  │  └────────────────────────────────────────────────┘   │ ║
║  │      │  │                                                         │ ║
║  │      │  │  10 total events registered  [Register for more →]    │ ║
║  │      │  │                                                         │ ║
║  └──────┘  └─────────────────────────────────────────────────────────┘ ║
║                                                                         ║
╚═════════════════════════════════════════════════════════════════════════╝
```

## Component Breakdown

### 1. Header Section
```
┌─────────────────────────────────────────────────────────┐
│  My Event Registrations                                 │
│  Track and manage your event registrations              │
│                                    [Browse Events] →    │
└─────────────────────────────────────────────────────────┘

Elements:
- Title: "My Event Registrations"
- Subtitle: Helpful description
- CTA Button: Browse Events (links to event_list)
```

### 2. Filter Tabs
```
┌─────────────────────────────────────────────────────────┐
│ [All Events] | [Registered] | [Participated]           │
└─────────────────────────────────────────────────────────┘

Behavior:
- Default: All tabs show all registrations
- Click tab: Filter table rows by status
- Active tab: Red underline + red text
- No page reload
```

### 3. Statistics Cards
```
┌──────────────┬──────────────┬──────────────┐
│  Total Evts  │  Registered  │  Certificates│
│      12      │      10      │      0       │
├──────────────┼──────────────┼──────────────┤
│   Blue       │   Green      │  Purple      │
│  Gradient Background                       │
└──────────────┴──────────────┴──────────────┘

Colors:
- Blue: Primary color
- Green: Success/Registered
- Purple: Accent color
```

### 4. Events Table

#### Column 1: Event Name
```
┌──────────────────────────────────────┐
│ 🎨 Art Fest 2025                     │
│    Art Club                          │
│                                      │
│ [Thumbnail/Avatar: 40x40px]          │
│ [Title with club name below]         │
└──────────────────────────────────────┘
```

#### Column 2: Date & Time
```
┌──────────────────────────────────────┐
│ Jan 18, 2026                         │
│ 2:00 PM                              │
│                                      │
│ [Full date format]                   │
│ [Time format]                        │
│ (Stacked vertically)                 │
└──────────────────────────────────────┘
```

#### Column 3: Venue
```
┌──────────────────────────────────────┐
│ 📍 Main Hall                         │
│                                      │
│ [Location icon]                      │
│ [Venue name, truncated if long]      │
└──────────────────────────────────────┘
```

#### Column 4: Status Badge
```
REGISTERED:
┌──────────────────────────────────────┐
│ ✓ Registered                         │
│ (Blue background)                    │
└──────────────────────────────────────┘

PARTICIPATED:
┌──────────────────────────────────────┐
│ ✓✓ Participated                      │
│ (Green background)                   │
└──────────────────────────────────────┘

CANCELLED:
┌──────────────────────────────────────┐
│ ✗ Cancelled                          │
│ (Red background)                     │
└──────────────────────────────────────┘
```

#### Column 5: Action Buttons
```
┌──────────────────────────────────────┐
│ [View]  [Cancel]                     │
│ (text links with hover effects)      │
│                                      │
│ View: Always available               │
│ Cancel: Only for future registrations│
└──────────────────────────────────────┘
```

### 5. Empty State
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                   📅 (Large Icon)                       │
│                                                         │
│            No event registrations yet                   │
│     Browse upcoming events and register to participate  │
│                                                         │
│              [🔍 Explore Events]                        │
│                                                         │
│          (Blue CTA button with icon)                    │
│                                                         │
└─────────────────────────────────────────────────────────┘

Shows when: my_events list is empty
CTA: Links to event_list page
```

### 6. Footer Summary
```
┌─────────────────────────────────────────────────────────┐
│ 12 total events registered                              │
│                            [Register for more events →] │
└─────────────────────────────────────────────────────────┘

Shows: Only when registrations exist
Stats: Count of all events in my_events
CTA: Links to event_list page
```

## User Interactions

### Scenario 1: View All Registrations
```
User Action: Page loads
→ Default view shows all events from my_events
→ Statistics cards display totals
→ Events table populated
→ Footer shows call-to-action
```

### Scenario 2: Filter by Status
```
User Action: Click "Registered" tab
→ "All" tab styling removed
→ "Registered" tab styling applied (red underline)
→ JavaScript runs filterRegistrations('registered')
→ Table rows with status != 'registered' hidden
→ Table rows with status == 'registered' shown
→ No page reload
```

### Scenario 3: View Event Details
```
User Action: Click [View] button
→ Navigate to event_detail view
→ Display full event information
→ User can view event, register, or unregister
```

### Scenario 4: Cancel Registration
```
User Action: Click [Cancel] button (only visible for future events)
→ Confirmation dialog appears
→ If confirmed: Navigate to event_unregister view
→ If cancelled: Stay on page
→ Registration removed from list
→ Redirected back to dashboard
```

### Scenario 5: Register for More
```
User Action: Click any "Browse Events" or "Explore Events" button
→ Navigate to event_list view
→ Display all upcoming events
→ User can browse and register for new events
```

## Responsive Design

### Desktop (> 1024px)
```
┌──────────────────────────────────────┐
│ Sidebar (fixed) │ Full Table Display │
│                 │ All columns visible│
│                 │ Hover effects work │
│                 │ Optimal spacing    │
└──────────────────────────────────────┘
```

### Tablet (640px - 1024px)
```
┌──────────────────────────────────────┐
│ Sidebar Hidden  │ Main Content       │
│ Toggle Button   │ Slightly narrower  │
│ Available       │ Horizontal scroll  │
│                 │ on table           │
└──────────────────────────────────────┘
```

### Mobile (< 640px)
```
┌──────────────────────────────────────┐
│ [≡] Sidebar Hidden                   │
│     Main Content Full Width          │
│                                      │
│ - Statistics: Stacked vertically     │
│ - Filter tabs: Horizontal scroll     │
│ - Table: Horizontal scroll           │
│ - Touch-friendly buttons (44x44)     │
└──────────────────────────────────────┘
```

## Color Palette

### Status Colors
```
Registered:     #3B82F6 (Blue)     - Primary action
Participated:   #10B981 (Green)    - Success state
Cancelled:      #EF4444 (Red)      - Alert/Warning
Neutral:        #9CA3AF (Gray)     - Disabled/Other
```

### UI Colors
```
Background:     #FFFFFF (White)
Text Primary:   #1F2937 (Dark Gray)
Text Secondary: #6B7280 (Medium Gray)
Borders:        #E5E7EB (Light Gray)
Hover:          #F3F4F6 (Lighter Gray)
```

### Accent Colors
```
Primary:        #DC2626 (Red)      - Links, CTAs
Info:           #3B82F6 (Blue)     - Information
Success:        #10B981 (Green)    - Success
Warning:        #F59E0B (Amber)    - Warning
```

## Filtering Algorithm

```javascript
filterRegistrations(filter) {
  ┌─ Get all .registration-row elements
  │
  ├─ Update tab styling
  │ └─ Remove all active states
  │ └─ Add active state to clicked tab
  │
  └─ Process each row
    ├─ Get row's data-status attribute
    ├─ Check if matches filter
    │ ├─ 'all' → show all rows
    │ ├─ 'registered' → show only status='registered'
    │ ├─ 'participated' → show only status='present'
    │ └─ other → hide row
    └─ Set row.style.display = '' or 'none'
}
```

## Data Mapping

### From Database to Template
```
EventRegistration Model
    ↓
    ├─ event (FK) → Event object
    ├─ student (FK) → User object
    ├─ status → 'REGISTERED' or 'CANCELLED'
    ├─ registered_at → DateTime
    └─ updated_at → DateTime

Attendance Model
    ↓
    ├─ session → AttendanceSession
    ├─ student → User
    ├─ status → 'PRESENT' or 'ABSENT'
    └─ recorded_at → DateTime

Combined in my_events list
    ↓
    {
      'event': Event object,
      'status': 'REGISTERED' | 'PRESENT' | 'CANCELLED',
      'get_status_display': User-friendly label,
      'sort_date': Event datetime
    }
```

## Accessibility Features

### Color Indicators
✓ Never rely on color alone
✓ Use icons (✓, ✓✓, ✗)
✓ Include text labels
✓ High contrast ratios

### Navigation
✓ Keyboard accessible
✓ Tab order logical
✓ Focus states visible
✓ Links descriptive

### Touch Targets
✓ Buttons: 44x44px minimum
✓ Adequate spacing
✓ Touch-friendly on mobile

### Media
✓ Alt text for images
✓ Icons semantic
✓ ARIA labels where needed

---

**This guide provides a comprehensive visual reference for the My Registrations page implementation.**
