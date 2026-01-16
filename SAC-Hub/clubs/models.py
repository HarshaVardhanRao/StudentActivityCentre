from django.db import models
from users.models import Club, User

# Create your models here.
class ClubReport(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='reports')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='submitted_reports')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='club_reports/', null=True, blank=True)
    content = models.TextField(blank=True, help_text="Report content if no file is uploaded")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Report: {self.title} - {self.club.name} ({self.status})"
