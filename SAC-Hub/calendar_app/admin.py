
from .models import CalendarEntry
from django.contrib import admin

@admin.register(CalendarEntry)
class CalendarEntryAdmin(admin.ModelAdmin):
	list_display = ("event", "entry_type", "date_time", "visible_to")
	list_filter = ("entry_type", "visible_to")
	search_fields = ("event__name",)
