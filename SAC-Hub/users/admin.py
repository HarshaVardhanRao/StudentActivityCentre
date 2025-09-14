from django.contrib import admin
from .models import User, Club, Department, Notification
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ("user", "message", "created_at", "read")
	list_filter = ("read", "created_at")
	search_fields = ("user__username", "message")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ("email", "username", "get_roles", "is_staff", "is_active")
	search_fields = ("email", "username", "roles")

	def get_roles(self, obj):
		return ", ".join(obj.roles) if isinstance(obj.roles, list) else str(obj.roles)
	get_roles.short_description = 'Roles'

	def save_model(self, request, obj, form, change):
		# Hash password if it's not already hashed
		if 'password' in form.changed_data:
			raw_password = form.cleaned_data.get('password')
			if raw_password and not raw_password.startswith('pbkdf2_'):
				obj.set_password(raw_password)
		super().save_model(request, obj, form, change)


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
	list_display = ("name", "get_coordinators", "advisor")
	search_fields = ("name",)
	filter_horizontal = ("coordinators",)

	def get_coordinators(self, obj):
		return ", ".join([str(u) for u in obj.coordinators.all()])
	get_coordinators.short_description = 'Coordinators'

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
	list_display = ("name",)
	search_fields = ("name",)
