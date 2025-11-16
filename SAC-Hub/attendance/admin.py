from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
	list_display = ("get_event", "student", "status", "timestamp")
	list_filter = ("status", "session__event")
	search_fields = ("student__email", "session__event__name")

	def get_event(self, obj):
		return obj.session.event if obj.session else None
	get_event.short_description = 'event'
	get_event.admin_order_field = 'session__event__name'
