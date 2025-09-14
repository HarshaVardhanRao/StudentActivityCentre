
from rest_framework import viewsets
from .models import CalendarEntry
from .serializers import CalendarEntrySerializer

class CalendarEntryViewSet(viewsets.ModelViewSet):
	queryset = CalendarEntry.objects.all()
	serializer_class = CalendarEntrySerializer
