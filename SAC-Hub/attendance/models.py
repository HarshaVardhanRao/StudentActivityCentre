
from django.db import models
from users.models import User
from events.models import Event
import uuid
from django.utils import timezone


class AttendanceStatus(models.TextChoices):
	PRESENT = 'PRESENT', 'Present'
	ABSENT = 'ABSENT', 'Absent'


class AttendanceSession(models.Model):
	"""A session for taking attendance for an Event. Multiple sessions per event allowed."""
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendance_sessions')
	label = models.CharField(max_length=128, blank=True, help_text='Session label (e.g., Period 1)')
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
	created_at = models.DateTimeField(auto_now_add=True)
	open_at = models.DateTimeField(null=True, blank=True, help_text='When attendance window opens')
	close_at = models.DateTimeField(null=True, blank=True, help_text='When attendance window was closed/submitted')
	submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_sessions')
	submitted_at = models.DateTimeField(null=True, blank=True)
	locked = models.BooleanField(default=False)
	attendance_code = models.CharField(max_length=32, unique=True, blank=True)

	def save(self, *args, **kwargs):
		if not self.attendance_code:
			# short unique code
			self.attendance_code = uuid.uuid4().hex[:12].upper()
		super().save(*args, **kwargs)

	def is_open(self):
		now = timezone.now()
		if self.locked:
			return False
		if self.open_at and now < self.open_at:
			return False
		if self.close_at and now > self.close_at:
			return False
		return True

	def __str__(self):
		return f"Session {self.label or self.id} for {self.event}"


class Attendance(models.Model):
	# Make session nullable for the initial migration so we can backfill existing rows.
	session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records', null=True, blank=True)
	student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
	status = models.CharField(max_length=10, choices=AttendanceStatus.choices)
	# Reference code for public verification of an attendance record
	ref_code = models.CharField(max_length=32, unique=True, blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('session', 'student')

	def __str__(self):
		return f"{self.student} - {self.session} ({self.status})"

	def save(self, *args, **kwargs):
		# Ensure a unique reference code exists for this attendance record.
		# Prefer a deterministic composite: eventid(last2) + sessionid(last2) + rollno(last4)
		if not self.ref_code:
			# Build components
			event_id = None
			session_id = None
			try:
				if self.session and getattr(self.session, 'event', None):
					event_id = int(self.session.event.id)
				if self.session:
					session_id = int(self.session.id)
			except Exception:
				event_id = None
				session_id = None

			roll = ''
			try:
				roll_raw = getattr(self.student, 'roll_no', '') or ''
				# Keep last up to 4 alphanumeric characters
				roll = ''.join(ch for ch in roll_raw if ch.isalnum())[-4:]
			except Exception:
				roll = ''

			parts = []
			if event_id is not None:
				parts.append(f"{event_id % 100:02d}")
			else:
				parts.append("00")
			if session_id is not None:
				parts.append(f"{session_id % 100:02d}")
			else:
				parts.append("00")
			if roll:
				parts.append(f"{roll}")
			else:
				# fallback to student id low digits
				try:
					parts.append(f"{self.student.id % 10000:04d}")
				except Exception:
					parts.append("0000")

			base = ''.join(parts).upper()

			# Ensure base is not too long (we allow space for a suffix)
			max_base_len = 28
			if len(base) > max_base_len:
				base = base[:max_base_len]

			# Ensure the reference code starts with an alphabetic character.
			# Choose a deterministic prefix letter derived from event/session/student ids.
			prefix_source = (event_id or session_id or (getattr(self.student, 'id', 0) if getattr(self, 'student', None) else 0))
			try:
				letter_idx = int(prefix_source) % 26
				prefix_letter = chr(ord('A') + letter_idx)
			except Exception:
				prefix_letter = 'A'

			if not base[0].isalpha():
				# Reserve one char for prefix; adjust base length accordingly
				base = (prefix_letter + base)[:max_base_len]

			candidate = base
			suffix = 0
			# Avoid matching self in case of update
			while Attendance.objects.filter(ref_code=candidate).exclude(pk=self.pk).exists():
				suffix += 1
				# append numeric suffix, keep within max_length
				suf = f"-{suffix}"
				truncate_len = 32 - len(suf)
				candidate = (base[:truncate_len] + suf).upper()

			self.ref_code = candidate
		super().save(*args, **kwargs)
