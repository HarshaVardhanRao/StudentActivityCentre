
from django.db import models
from users.models import Club, Department, User, Notification

class EventStatus(models.TextChoices):
	DRAFT = 'DRAFT', 'Draft'
	PENDING = 'PENDING', 'Pending Approval'
	APPROVED = 'APPROVED', 'Approved'
	REJECTED = 'REJECTED', 'Rejected'
	COMPLETED = 'COMPLETED', 'Completed'

class Event(models.Model):
	name = models.CharField(max_length=200)
	event_type = models.CharField(max_length=100)
	description = models.TextField(blank=True)
	date_time = models.DateTimeField()
	venue = models.CharField(max_length=200)
	resources = models.TextField(blank=True)
	club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
	department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
	organizers = models.ManyToManyField(User, related_name='organized_events')
	status = models.CharField(max_length=20, choices=EventStatus.choices, default=EventStatus.DRAFT)
	approval_chain = models.JSONField(default=list, blank=True, help_text='List of approval steps and statuses')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		is_new = self._state.adding
		old_status = None
		if not is_new:
			old = Event.objects.get(pk=self.pk)
			old_status = old.status
		super().save(*args, **kwargs)

		# Notify club coordinators on new event submission
		if is_new:
			for coordinator in self.club.coordinators.all():
				Notification.objects.create(
					user=coordinator,
					message=f"New event '{self.name}' has been submitted for your club."
				)

		# Notify on status change
		if not is_new and old_status != self.status:
			# Notify all organizers
			for organizer in self.organizers.all():
				Notification.objects.create(
					user=organizer,
					message=f"Status of event '{self.name}' changed to {self.status}."
				)
			# Notify club coordinators
			for coordinator in self.club.coordinators.all():
				Notification.objects.create(
					user=coordinator,
					message=f"Status of event '{self.name}' changed to {self.status}."
				)

class CollaborationRequest(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='collaboration_requests')
	requesting_department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='collab_requests')
	status = models.CharField(max_length=20, choices=[('PENDING','Pending'),('APPROVED','Approved'),('REJECTED','Rejected')], default='PENDING')
	approval_chain = models.JSONField(default=list, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.requesting_department} requests for {self.event}"
