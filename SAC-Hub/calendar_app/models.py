
from django.db import models
from events.models import Event

class CalendarEntryType(models.TextChoices):
	CLUB_EVENT = 'CLUB_EVENT', 'Club Event'
	DEPARTMENT_EVENT = 'DEPARTMENT_EVENT', 'Department Event'
	NATIONAL_DAY = 'NATIONAL_DAY', 'National Day/Week'

class CalendarEntry(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='calendar_entries')
	entry_type = models.CharField(max_length=30, choices=CalendarEntryType.choices)
	date_time = models.DateTimeField()
	visible_to = models.CharField(max_length=100, default='all', help_text='Visibility: all, club, department, etc.')

	def __str__(self):
		return f"{self.event} - {self.entry_type}"
