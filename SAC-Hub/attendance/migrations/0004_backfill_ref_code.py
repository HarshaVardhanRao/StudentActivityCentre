from django.db import migrations


def generate_ref_code(apps, schema_editor):
    Attendance = apps.get_model('attendance', 'Attendance')
    Session = apps.get_model('attendance', 'AttendanceSession')
    # iterate attendance records without ref_code
    qs = Attendance.objects.filter(ref_code__isnull=True) | Attendance.objects.filter(ref_code='')
    for att in qs:
        # Build base similar to model logic
        event_id = None
        session_id = None
        try:
            if att.session_id:
                session = Session.objects.filter(id=att.session_id).first()
                if session and getattr(session, 'event_id', None):
                    event_id = int(session.event_id)
                if session:
                    session_id = int(session.id)
        except Exception:
            event_id = None
            session_id = None

        roll = ''
        try:
            roll_raw = getattr(att, 'student_id', None)
            # we don't have access to student.roll_no via historical model reliably,
            # so fallback to using student_id digits
            if roll_raw is not None:
                roll = f"{int(roll_raw) % 10000:04d}"
        except Exception:
            roll = ''

        parts = []
        parts.append(f"{(event_id % 100) if event_id is not None else 0:02d}")
        parts.append(f"{(session_id % 100) if session_id is not None else 0:02d}")
        parts.append(roll or f"{(att.student_id % 10000):04d}")
        base = ''.join(parts).upper()

        candidate = base
        suffix = 0
        while Attendance.objects.filter(ref_code=candidate).exclude(pk=att.pk).exists():
            suffix += 1
            suf = f"-{suffix}"
            truncate_len = 32 - len(suf)
            candidate = (base[:truncate_len] + suf).upper()

        att.ref_code = candidate
        att.save()


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_attendance_ref_code'),
    ]

    operations = [
        migrations.RunPython(generate_ref_code, migrations.RunPython.noop),
    ]
