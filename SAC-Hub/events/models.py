
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

class EventRegistration(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
	student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
	registered_at = models.DateTimeField(auto_now_add=True)
	notes = models.TextField(blank=True, help_text='Optional notes from the student')
	
	class Meta:
		unique_together = ['event', 'student']  # Prevent duplicate registrations
		
	def __str__(self):
		return f"{self.student.get_full_name()} registered for {self.event.name}"

class EventAssociation(models.Model):
	"""Model for event associations with departments or clubs"""
	ASSOCIATION_TYPE_CHOICES = [
		('DEPARTMENT', 'Department Association'),
		('CLUB', 'Club Association'),
	]
	
	STATUS_CHOICES = [
		('PENDING', 'Pending Approval'),
		('APPROVED', 'Approved'),
		('REJECTED', 'Rejected'),
	]
	
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='associations')
	association_type = models.CharField(max_length=20, choices=ASSOCIATION_TYPE_CHOICES)
	
	# Either department or club will be filled, not both
	department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, related_name='event_associations')
	club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True, related_name='event_associations')
	
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
	requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_associations')
	approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_associations')
	approval_notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		unique_together = [
			['event', 'department'],
			['event', 'club']
		]
	
	def __str__(self):
		if self.association_type == 'DEPARTMENT':
			return f"{self.event.name} - {self.department.name} Association"
		else:
			return f"{self.event.name} - {self.club.name} Association"
	
	def get_associated_entity(self):
		"""Return the associated department or club"""
		return self.department if self.association_type == 'DEPARTMENT' else self.club
	
	def save(self, *args, **kwargs):
		is_new = self._state.adding
		super().save(*args, **kwargs)
		
		# Notify relevant officers when new association is requested
		if is_new:
			if self.association_type == 'DEPARTMENT' and self.department:
				# Notify department admins and coordinators
				all_users = User.objects.all()
				dept_officers = [user for user in all_users if 
					'DEPARTMENT_ADMIN' in (user.roles or []) and user.department == self.department]
				
				for officer in dept_officers:
					Notification.objects.create(
						user=officer,
						message=f"New association request for event '{self.event.name}' with {self.department.name} department."
					)
			
			elif self.association_type == 'CLUB' and self.club:
				# Notify club coordinators and advisors
				for coordinator in self.club.coordinators.all():
					Notification.objects.create(
						user=coordinator,
						message=f"New association request for event '{self.event.name}' with {self.club.name} club."
					)
				
				if self.club.advisor:
					Notification.objects.create(
						user=self.club.advisor,
						message=f"New association request for event '{self.event.name}' with {self.club.name} club."
					)

class EventCollaboration(models.Model):
	"""Model for event collaborations (different from associations - more formal partnerships)"""
	STATUS_CHOICES = [
		('PENDING', 'Pending Approval'),
		('APPROVED', 'Approved'),
		('REJECTED', 'Rejected'),
	]
	
	COLLABORATION_TYPE_CHOICES = [
		('DEPARTMENT', 'Department Collaboration'),
		('CLUB', 'Club Collaboration'),
	]
	
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='collaborations')
	collaboration_type = models.CharField(max_length=20, choices=COLLABORATION_TYPE_CHOICES)
	
	# Either department or club will be filled, not both
	department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True, related_name='event_collaborations')
	club = models.ForeignKey(Club, on_delete=models.CASCADE, null=True, blank=True, related_name='event_collaborations')
	
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
	collaboration_details = models.TextField(help_text='Details about the collaboration (resources, responsibilities, etc.)')
	requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_collaborations')
	approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_collaborations')
	approval_notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	
	class Meta:
		unique_together = [
			['event', 'department'],
			['event', 'club']
		]
	
	def __str__(self):
		if self.collaboration_type == 'DEPARTMENT':
			return f"{self.event.name} - {self.department.name} Collaboration"
		else:
			return f"{self.event.name} - {self.club.name} Collaboration"
	
	def get_collaborating_entity(self):
		"""Return the collaborating department or club"""
		return self.department if self.collaboration_type == 'DEPARTMENT' else self.club
	
	def save(self, *args, **kwargs):
		is_new = self._state.adding
		super().save(*args, **kwargs)
		
		# Notify relevant officers when new collaboration is requested
		if is_new:
			if self.collaboration_type == 'DEPARTMENT' and self.department:
				# Notify department admins
				all_users = User.objects.all()
				dept_officers = [user for user in all_users if 
					'DEPARTMENT_ADMIN' in (user.roles or []) and user.department == self.department]
				
				for officer in dept_officers:
					Notification.objects.create(
						user=officer,
						message=f"New collaboration request for event '{self.event.name}' with {self.department.name} department."
					)
			
			elif self.collaboration_type == 'CLUB' and self.club:
				# Notify club coordinators and advisors
				for coordinator in self.club.coordinators.all():
					Notification.objects.create(
						user=coordinator,
						message=f"New collaboration request for event '{self.event.name}' with {self.club.name} club."
					)
				
				if self.club.advisor:
					Notification.objects.create(
						user=self.club.advisor,
						message=f"New collaboration request for event '{self.event.name}' with {self.club.name} club."
					)
