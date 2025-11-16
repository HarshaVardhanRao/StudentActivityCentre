from django.db import migrations, models


def normalize_ref_codes(apps, schema_editor):
    Attendance = apps.get_model('attendance', 'Attendance')
    Session = apps.get_model('attendance', 'AttendanceSession')

    def make_candidate(att):
        # Re-implement generation logic used in model to ensure alpha prefix
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
            # Try to get roll_no via relation; fallback to student_id digits
            stud = getattr(att, 'student', None)
            if stud is not None and getattr(stud, 'roll_no', None):
                roll_raw = getattr(stud, 'roll_no') or ''
                roll = ''.join(ch for ch in roll_raw if ch.isalnum())[-4:]
        except Exception:
            roll = ''

        parts = []
        parts.append(f"{(event_id % 100) if event_id is not None else 0:02d}")
        parts.append(f"{(session_id % 100) if session_id is not None else 0:02d}")
        parts.append(roll or f"{(getattr(att, 'student_id', 0) % 10000):04d}")
        base = ''.join(parts).upper()

        max_base_len = 28
        if len(base) > max_base_len:
            base = base[:max_base_len]

        prefix_source = (event_id or session_id or (getattr(att, 'student_id', 0) or 0))
        try:
            letter_idx = int(prefix_source) % 26
            prefix_letter = chr(ord('A') + letter_idx)
        except Exception:
            prefix_letter = 'A'

        if not base[0].isalpha():
            base = (prefix_letter + base)[:max_base_len]

        candidate = base
        suffix = 0
        # Ensure uniqueness
        while Attendance.objects.filter(ref_code=candidate).exclude(pk=att.pk).exists():
            suffix += 1
            suf = f"-{suffix}"
            truncate_len = 32 - len(suf)
            candidate = (base[:truncate_len] + suf).upper()

        return candidate

    # Update records whose ref_code is null/empty or does not start with a letter
    qs = Attendance.objects.filter(models.Q(ref_code__isnull=True) | models.Q(ref_code='') | ~models.Q(ref_code__regex=r'^[A-Za-z]'))
    for att in qs:
        att.ref_code = make_candidate(att)
        att.save()


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0005_make_ref_code_nonnull_unique'),
    ]

    operations = [
        migrations.RunPython(normalize_ref_codes, migrations.RunPython.noop),
    ]
