from django.contrib import admin
from .models import Event, CollaborationRequest

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
	list_display = ("name", "event_type", "date_time", "status", "club")
	search_fields = ("name", "event_type")
	list_filter = ("status", "event_type")

@admin.register(CollaborationRequest)
class CollaborationRequestAdmin(admin.ModelAdmin):
	list_display = ("event", "requesting_department", "status")
	list_filter = ("status",)

