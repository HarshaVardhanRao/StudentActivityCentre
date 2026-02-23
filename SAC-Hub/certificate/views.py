from django.shortcuts import render
from django.http import FileResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from PIL import Image, ImageDraw, ImageFont, ImageColor
from io import BytesIO
import zipfile
import pandas as pd
import os
from datetime import datetime

# Club options with their corresponding certificate templates
CLUB_OPTIONS = [
    {"name": "Tech Club", "certificate_template": "tech_club.jpg"},
    {"name": "Sports Club", "certificate_template": "sports_club.jpg"},
    {"name": "Cultural Club", "certificate_template": "cultural_club.jpg"},
    {"name": "Science Club", "certificate_template": "science_club.jpg"},
]


# Default layout and styling (adjust as needed)
DEFAULT_LAYOUT = {
    # Provide start/end X so text is centered inside its own field span
    "name": {"y": 1020, "x1": 633, "x2": 1258, "font_size": 45, "color": "#021c77", "bold": True},
    "department": {"y": 1093, "x1": 214, "x2": 1040, "font_size": 40, "color": "black", "bold": True},
    "event": {"y": 1160, "x1": 773, "x2": 1257, "font_size": 30, "color": "black", "bold": True},
    "date": {"y": 1237, "x1": 213, "x2": 453, "font_size": 40, "color": "black", "bold": True},
    "club": {"y": 1229, "x1": 756, "x2": 1260, "font_size": 40, "color": "black", "bold": True},
}


@login_required
def home(request):
    """Landing page showing student's participated events with certificate download"""
    from attendance.models import Attendance
    from events.models import Event
    
    # Get events where student has attendance marked as PRESENT
    attended_sessions = Attendance.objects.filter(
        student=request.user,
        status='PRESENT'
    ).select_related('session__event')
    
    # Extract unique events
    attended_events = []
    seen_event_ids = set()
    
    for attendance in attended_sessions:
        if attendance.session and attendance.session.event:
            event = attendance.session.event
            if event.id not in seen_event_ids:
                seen_event_ids.add(event.id)
                attended_events.append({
                    'event': event,
                    'attendance_date': attendance.timestamp
                })
    
    # Sort by event date (most recent first)
    attended_events.sort(key=lambda x: x['event'].date_time, reverse=True)
    
    context = {
        'attended_events': attended_events,
        'clubs': CLUB_OPTIONS
    }
    return render(request, 'certificate/index.html', context)


@login_required
def generate_certificates(request):
    """Generate certificates for single person or bulk generation from Excel file"""
    if request.method == "POST":
        # Get mandatory fields
        event = request.POST.get('event', '')
        date = request.POST.get('date', '')
        club_name = request.POST.get('club_name', '')
        
        template_file = get_template_for_club(club_name)
        
        # Check if it's bulk generation (Excel file)
        excel_file = request.FILES.get('excel_file')
        
        if excel_file:
            # Bulk generation from Excel file
            df = pd.read_excel(excel_file)
            
            # Create a zip file to store certificates
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for index, row in df.iterrows():
                    name = row.get('name', row.get('Name', ''))
                    dept = row.get('department', row.get('Department', ''))
                    
                    # Generate certificate with mandatory fields from form
                    cert_buffer = create_certificate_pdf(name, dept, event, date, club_name, template_file)
                    
                    # Add the certificate to the zip file
                    zip_file.writestr(f"{name}_{event}_certificate.pdf", cert_buffer.getvalue())
            
            # Prepare the zip file for download
            zip_buffer.seek(0)
            response = FileResponse(zip_buffer, as_attachment=True, filename=f"certificates_{datetime.now().strftime('%d%m%Y_%H%M%S')}.zip")
            return response
        else:
            # Single certificate generation
            name = request.POST.get('name', '')
            dept = request.POST.get('department', '')
            
            # Generate single certificate
            cert_buffer = create_certificate_pdf(name, dept, event, date, club_name, template_file)
            
            # Return as download
            response = FileResponse(cert_buffer, as_attachment=True, filename=f"{name}_{event}_certificate.pdf")
            return response
    
    # GET request - show form with club options
    context = {
        'clubs': CLUB_OPTIONS
    }
    return render(request, 'certificate/generate_certificates.html', context)


def get_template_for_club(club_name: str) -> str:
    """Return the template filename for a given club, or a default sample."""
    for club in CLUB_OPTIONS:
        if club["name"] == club_name:
            return club["certificate_template"]
    return "sample.jpg"


def load_font(size: int, bold: bool = False):
    """Load Roboto from project static; fallback to DejaVu/ default."""
    static_dir = os.path.join(settings.BASE_DIR, "static")
    roboto_file = "Roboto-Bold.ttf" if bold else "Roboto-Regular.ttf"
    roboto_path = os.path.join(static_dir, roboto_file)
    dejavu = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    for path in (roboto_path, dejavu):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def create_certificate_pdf(name, department, event, date, club_name, template_file, layout=None):
    """Create a certificate PDF with centered text alignment on the template image."""
    layout = layout or DEFAULT_LAYOUT

    # Resolve template path - check if it's an absolute path (uploaded file) or static file
    if os.path.isabs(template_file) and os.path.exists(template_file):
        # Use uploaded file path directly
        template_path = template_file
    else:
        # Use static template file
        template_path = os.path.join(settings.BASE_DIR, 'certificate', 'static', template_file)
        if not os.path.exists(template_path):
            template_path = os.path.join(settings.BASE_DIR, 'certificate', 'static', 'sample.jpg')

    # Open image in RGB to ensure PDF compatibility
    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    img_width, _ = image.size

    # Format date to dd-mm-yyyy when possible
    def format_date_value(raw):
        if raw is None:
            return ""
        if isinstance(raw, datetime):
            return raw.strftime("%d-%m-%Y")
        text = str(raw)
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(text, fmt).strftime("%d-%m-%Y")
            except ValueError:
                continue
        return text

    # Helper to draw centered text using layout settings
    def draw_field(value, field_key):
        field = layout.get(field_key, {})
        y_pos = field.get("y", 0)
        font_size = field.get("font_size", 40)
        color = field.get("color", "black")
        try:
            color = ImageColor.getrgb(color)
        except Exception:
            color = "black"
        bold = field.get("bold", False)
        x1 = field.get("x1", 0)
        x2 = field.get("x2", img_width)

        # Clamp to image bounds
        x1 = max(0, min(x1, img_width))
        x2 = max(0, min(x2, img_width))
        span = max(1, x2 - x1)

        text = str(value) if value is not None else ""

        # If name is long, shrink font to keep centered text within span
        if field_key == "name" and len(text) > 23:
            font_size = 35

        font = load_font(font_size, bold)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]

        # Center inside the provided field span
        x_pos = x1 + max(0, (span - text_width) // 2)
        draw.text((x_pos, y_pos), text, fill=color, font=font)

    # Draw all fields
    draw_field(name, "name")
    draw_field(department, "department")
    draw_field(event, "event")
    draw_field(format_date_value(date), "date")
    draw_field(club_name, "club")

    # Save to PDF buffer
    buffer = BytesIO()
    image.save(buffer, format="PDF", resolution=300)
    buffer.seek(0)
    return buffer


@login_required
def generate_certificate(request):
    """Sample single certificate endpoint using shared PDF generator."""
    sample = {
        "name": "Gundala Charitha",
        "department": "Electronics & Communication Engineering",
        "event": "Tech Quest",
        "date": "2026-01-03",
        "club_name": "Tech Club",
    }

    template_file = get_template_for_club(sample["club_name"])
    cert_buffer = create_certificate_pdf(
        sample["name"],
        sample["department"],
        sample["event"],
        sample["date"],
        sample["club_name"],
        template_file,
    )

    return FileResponse(cert_buffer, as_attachment=True, filename="certificate.pdf")


@login_required
def download_event_certificate(request, event_id):
    """Download certificate for a specific event the student attended"""
    from events.models import Event
    from attendance.models import Attendance
    from django.shortcuts import get_object_or_404
    from django.http import HttpResponseForbidden
    
    # Get the event
    event = get_object_or_404(Event, id=event_id)
    
    # Verify student attended this event
    attendance_exists = Attendance.objects.filter(
        student=request.user,
        session__event=event,
        status='PRESENT'
    ).exists()
    
    if not attendance_exists:
        return HttpResponseForbidden("You did not attend this event.")
    
    # Get student details
    student_name = request.user.get_full_name() or request.user.username
    department = request.user.department.name if request.user.department else "Student"
    
    # Get club name for template
    club_name = event.club.name if event.club else "MITS SAC"
    
    # Get appropriate template from club's certificate_template field
    if event.club and hasattr(event.club, 'certificate_template') and event.club.certificate_template:
        # Use uploaded file path
        template_file = event.club.certificate_template.path
    else:
        # Use static template
        template_file = get_template_for_club(club_name)
    
    # Generate certificate
    cert_buffer = create_certificate_pdf(
        student_name,
        department,
        event.name,
        event.date_time,
        club_name,
        template_file,
    )
    
    # Return as download
    filename = f"{student_name}_{event.name}_certificate.pdf".replace(" ", "_")
    return FileResponse(cert_buffer, as_attachment=True, filename=filename)
