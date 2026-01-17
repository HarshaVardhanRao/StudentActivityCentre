from django.contrib import admin
from .models import Event, CollaborationRequest, EventReport, EventAssociation, EventCollaboration, EventRegistration

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
	list_display = ("name", "event_type", "date_time", "status", "club")
	search_fields = ("name", "event_type")
	list_filter = ("status", "event_type")

@admin.register(CollaborationRequest)
class CollaborationRequestAdmin(admin.ModelAdmin):
	list_display = ("event", "requesting_department", "status")
	list_filter = ("status",)

@admin.register(EventReport)
class EventReportAdmin(admin.ModelAdmin):
	list_display = ("title", "event", "status", "submitted_by", "created_at")
	search_fields = ("title", "event__name")
	list_filter = ("status", "created_at")
	readonly_fields = ("created_at", "updated_at", "submitted_at", "approved_at")
	fieldsets = (
		("Report Details", {
			"fields": ("event", "title", "description", "submitted_by")
		}),
		("Event Metrics", {
			"fields": ("total_attendees", "expected_attendees", "budget_allocated", "budget_used")
		}),
		("Event Analysis", {
			"fields": ("highlights", "challenges", "lessons_learned")
		}),
		("Approval", {
			"fields": ("status", "approved_by", "approval_notes", "file")
		}),
		("Timestamps", {
			"fields": ("created_at", "updated_at", "submitted_at", "approved_at"),
			"classes": ("collapse",)
		}),
	)

@admin.register(EventAssociation)
class EventAssociationAdmin(admin.ModelAdmin):
	list_display = ("event", "association_type", "status", "requested_by")
	list_filter = ("status", "association_type")

@admin.register(EventCollaboration)
class EventCollaborationAdmin(admin.ModelAdmin):
	list_display = ("event", "collaboration_type", "status", "requested_by")
	list_filter = ("status", "collaboration_type")

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
	list_display = ("event", "student", "status", "registered_at")
	list_filter = ("status", "registered_at")
	search_fields = ("event__name", "student__username")
