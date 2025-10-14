
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
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_events', help_text='User who created this event')
	status = models.CharField(max_length=20, choices=EventStatus.choices, default=EventStatus.PENDING)
	approval_chain = models.JSONField(default=list, blank=True, help_text='List of approval steps and statuses')
	approval_notes = models.TextField(blank=True, help_text='Notes from administrators during approval process')
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

		# Notify administrators on new event submission for approval
		if is_new and self.status == 'PENDING':
			# Get all administrators and SAC coordinators
			all_users = User.objects.all()
			admins = [user for user in all_users if 'ADMIN' in (user.roles or []) or 'SAC_COORDINATOR' in (user.roles or [])]
			
			for admin in admins:
				Notification.objects.create(
					user=admin,
					message=f"New event '{self.name}' by {self.created_by.get_full_name() if self.created_by else 'Unknown'} is pending approval."
				)

		# Notify club coordinators on new event submission
		if is_new:
			for coordinator in self.club.coordinators.all():
				Notification.objects.create(
					user=coordinator,
					message=f"New event '{self.name}' has been submitted for your club."
				)

		# Notify on status change
		if not is_new and old_status != self.status:
			# Notify event creator
			if self.created_by:
				Notification.objects.create(
					user=self.created_by,
					message=f"Your event '{self.name}' status changed to {self.get_status_display()}."
				)
			
			# Notify all organizers
			for organizer in self.organizers.all():
				Notification.objects.create(
					user=organizer,
					message=f"Status of event '{self.name}' changed to {self.get_status_display()}."
				)
			
			# Notify club coordinators
			for coordinator in self.club.coordinators.all():
				Notification.objects.create(
					user=coordinator,
					message=f"Status of event '{self.name}' changed to {self.get_status_display()}."
				)

class CollaborationRequest(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='collaboration_requests')
	requesting_department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='collab_requests')
	status = models.CharField(max_length=20, choices=[('PENDING','Pending'),('APPROVED','Approved'),('REJECTED','Rejected')], default='PENDING')
	approval_chain = models.JSONField(default=list, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.requesting_department} requests for {self.event}"
