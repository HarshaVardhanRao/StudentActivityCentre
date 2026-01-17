
from rest_framework import viewsets
from .models import Event, CollaborationRequest, EventReport
from .serializers import EventSerializer, CollaborationRequestSerializer, EventReportSerializer

class EventViewSet(viewsets.ModelViewSet):
	queryset = Event.objects.all()
	serializer_class = EventSerializer

class CollaborationRequestViewSet(viewsets.ModelViewSet):
	queryset = CollaborationRequest.objects.all()
	serializer_class = CollaborationRequestSerializer

class EventReportViewSet(viewsets.ModelViewSet):
	queryset = EventReport.objects.all()
	serializer_class = EventReportSerializer
	
	def get_queryset(self):
		"""Filter reports based on user role"""
		user = self.request.user
		queryset = EventReport.objects.all()
		
		if not user.is_authenticated:
			return queryset.none()
		
		user_roles = user.roles or []
		
		# Club coordinators see reports from their club's events
		if 'CLUB_COORDINATOR' in user_roles:
			user_clubs = user.coordinated_clubs.all()
			queryset = queryset.filter(event__club__in=user_clubs)
		
		# Club advisors see reports from their club's events
		elif 'CLUB_ADVISOR' in user_roles:
			user_clubs = user.advised_clubs.all()
			queryset = queryset.filter(event__club__in=user_clubs)
		
		# Department admins see reports from their department's events
		elif 'ADMIN' in user_roles and 'SAC_COORDINATOR' not in user_roles:
			if hasattr(user, 'department') and user.department:
				queryset = queryset.filter(event__department=user.department)
		
		# SAC coordinators see all reports
		elif 'SAC_COORDINATOR' in user_roles:
			pass
		
		# Other users can only see their own reports
		else:
			queryset = queryset.filter(submitted_by=user)
		
		return queryset
