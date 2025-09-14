
from django.db import models
from users.models import User
from events.models import Event

class AttendanceStatus(models.TextChoices):
	PRESENT = 'PRESENT', 'Present'
	ABSENT = 'ABSENT', 'Absent'

class Attendance(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
	student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
	status = models.CharField(max_length=10, choices=AttendanceStatus.choices)
	timestamp = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('event', 'student')

	def __str__(self):
		return f"{self.student} - {self.event} ({self.status})"
