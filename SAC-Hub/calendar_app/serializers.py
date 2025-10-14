from rest_framework import serializers
from .models import CalendarEntry

class CalendarEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEntry
        fields = '__all__'
