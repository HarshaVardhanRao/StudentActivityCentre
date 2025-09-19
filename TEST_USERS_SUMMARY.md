# Student Activity Centre - Test Users Summary

## Quick Reference
**Default Password for ALL users:** `testpass123`

## Student Users (2)
| Username | Role | Roll No | Department |
|----------|------|---------|------------|
| ST2024001 | Student | ST2024001 | Computer Science |
| ST2024002 | Student | ST2024002 | Electronics & Communication |

## Administrative Roles
| Username | Role | Department | Notes |
|----------|------|------------|-------|
| admin | Admin | None | System Administrator |
| sac_coordinator | SAC Coordinator | Computer Science | Also has Student role |
| co_coordinator | Co-Coordinator | Electronics & Communication | Also has Student role |
| dept_admin | Department Admin | Computer Science | Department level admin |

## Leadership Roles (Student-based)
| Username | Role | Roll No | Department |
|----------|------|---------|------------|
| PR2024001 | President | PR2024001 | Computer Science |
| VP2024001 | SVP (Senior VP) | VP2024001 | Electronics & Communication |
| SEC2024001 | **Secretary** | SEC2024001 | Mechanical Engineering |
| TR2024001 | Treasurer | TR2024001 | Computer Science |
| DVP2024001 | Department VP | DVP2024001 | Electronics & Communication |

## Club & Event Roles
| Username | Role | Roll No | Department | Notes |
|----------|------|---------|------------|-------|
| CC2024001 | Club Coordinator | CC2024001 | Computer Science | Manages Technology Club |
| club_advisor | Club Advisor | None | Computer Science | Faculty role |
| EO2024001 | Event Organizer | EO2024001 | Mechanical Engineering | Student role |
| SV2024001 | Student Volunteer | SV2024001 | Electronics & Communication | Student role |

## Faculty
| Username | Role | Department |
|----------|------|------------|
| faculty | Faculty | Mechanical Engineering |
| club_advisor | Club Advisor + Faculty | Computer Science |

## Testing the Secretary Role
The **Secretary role** can be tested with:
- **Username:** `SEC2024001`
- **Password:** `testpass123`
- **Access:** 
  - Student Dashboard: http://localhost:8000/dashboard/
  - Secretary Dashboard: http://localhost:8000/dashboard/secretary/
  - Secretary API: http://localhost:8000/api/dashboard/secretary/

## Login Instructions
1. Go to: http://localhost:8000/login/
2. Use any username from the list above
3. Password: `testpass123`
4. Each user will see appropriate dashboards based on their roles

## Key Features Tested
- ✅ Secretary role assigned to student user (SEC2024001)
- ✅ Multiple role assignments (many users have both primary role + STUDENT)
- ✅ Proper username assignment (students use roll numbers)
- ✅ Department associations
- ✅ Club coordinator assignments
- ✅ Faculty and administrative roles

## Departments Created
- Computer Science
- Electronics & Communication 
- Mechanical Engineering

## Clubs Created
- Technology Club (with coordinator and advisor assigned)
- Cultural Club
- Sports Club