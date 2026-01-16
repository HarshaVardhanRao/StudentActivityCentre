
from django.db import models
from django.contrib.auth.models import AbstractUser

class Department(models.Model):
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.name


class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    coordinators = models.ManyToManyField(
        'User', blank=True, related_name='coordinated_clubs'
    )
    logo = models.ImageField(upload_to='club_logos/', null=True, blank=True)
    advisor = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='advised_clubs', limit_choices_to={'roles': 'FACULTY'}
    )

    def __str__(self):
        return self.name


class Role(models.TextChoices):
	SAC_COORDINATOR = 'SAC_COORDINATOR', 'SAC Coordinator'
	CO_COORDINATOR = 'CO_COORDINATOR', 'Co-Coordinator'
	DEPARTMENT_ADMIN = 'DEPARTMENT_ADMIN', 'Department Admin'
	PRESIDENT = 'PRESIDENT', 'President'
	SVP = 'SVP', 'Senior VP'
	SECRETARY = 'SECRETARY', 'Secretary'
	TREASURER = 'TREASURER', 'Treasurer'
	DEPARTMENT_VP = 'DEPARTMENT_VP', 'Department VP'
	CLUB_COORDINATOR = 'CLUB_COORDINATOR', 'Club Coordinator'
	CLUB_ADVISOR = 'CLUB_ADVISOR', 'Club Advisor'
	EVENT_ORGANIZER = 'EVENT_ORGANIZER', 'Event Organizer'
	STUDENT_VOLUNTEER = 'STUDENT_VOLUNTEER', 'Student Volunteer'
	STUDENT = 'STUDENT', 'Student'
	FACULTY = 'FACULTY', 'Faculty'
	ADMIN = 'ADMIN', 'Admin'

class User(AbstractUser):
	# For students, roll_no is used as username
	roll_no = models.CharField(max_length=20, unique=True, null=True, blank=True, help_text='Student Roll Number (used as username for students)')
	email = models.EmailField(unique=True, null=True, blank=True)
	contact_number = models.CharField(max_length=15, blank=True, null=True)
	roles = models.JSONField(default=list, help_text='List of roles for the user')
	department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
	clubs = models.ManyToManyField(Club, blank=True, related_name='members')
	
	# Academic information for students
	year_of_study = models.CharField(max_length=20, blank=True, null=True, help_text='Year of study (e.g., 1st Year, 2nd Year, 3rd Year, 4th Year)')
	section = models.CharField(max_length=10, blank=True, null=True, help_text='Section (e.g., A, B, C)')
	
	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = ['email', 'roll_no']

	def save(self, *args, **kwargs):
		# If user is a student, set username to roll_no
		if Role.STUDENT in self.roles and self.roll_no:
			self.username = self.roll_no
		super().save(*args, **kwargs)

	def __str__(self):
		if Role.STUDENT in self.roles and self.roll_no:
			return f"{self.get_full_name()} ({self.roll_no})"
		return f"{self.get_full_name()} ({self.email})"

class Notification(models.Model):
	user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='notifications')
	message = models.TextField()
	important = models.BooleanField(default=False, help_text='Mark notification as important')
	created_at = models.DateTimeField(auto_now_add=True)
	read = models.BooleanField(default=False)

	def __str__(self):
		return f"To: {self.user} | {self.message[:40]}{'...' if len(self.message) > 40 else ''}"