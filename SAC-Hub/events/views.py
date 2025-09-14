
from rest_framework import viewsets
from .models import Event, CollaborationRequest
from .serializers import EventSerializer, CollaborationRequestSerializer

class EventViewSet(viewsets.ModelViewSet):
	queryset = Event.objects.all()
	serializer_class = EventSerializer

class CollaborationRequestViewSet(viewsets.ModelViewSet):
	queryset = CollaborationRequest.objects.all()
	serializer_class = CollaborationRequestSerializer
