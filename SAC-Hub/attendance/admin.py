from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
	list_display = ("event", "student", "status", "timestamp")
	list_filter = ("status", "event")
	search_fields = ("student__email", "event__name")
