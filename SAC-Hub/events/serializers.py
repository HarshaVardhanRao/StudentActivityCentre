from rest_framework import serializers
from .models import Event, CollaborationRequest, EventReport

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class CollaborationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollaborationRequest
        fields = '__all__'

class EventReportSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True, allow_null=True)
    event_name = serializers.CharField(source='event.name', read_only=True)
    
    class Meta:
        model = EventReport
        fields = [
            'id', 'event', 'event_name', 'title', 'description',
            'submitted_by', 'submitted_by_name', 'status',
            'total_attendees', 'expected_attendees', 'budget_used', 'budget_allocated',
            'highlights', 'challenges', 'lessons_learned',
            'file', 'approved_by', 'approved_by_name', 'approval_notes',
            'created_at', 'updated_at', 'submitted_at', 'approved_at'
        ]
