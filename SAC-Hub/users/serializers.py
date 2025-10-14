#import serializers
from rest_framework import serializers


from .models import User, Club, Department, Notification
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
from rest_framework import serializers
from .models import User, Club, Department

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class ClubSerializer(serializers.ModelSerializer):
    coordinators = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)

    class Meta:
        model = Club
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.ListField(child=serializers.CharField(), required=False)
    clubs = serializers.PrimaryKeyRelatedField(many=True, queryset=Club.objects.all(), required=False)

    class Meta:
        model = User
        fields = '__all__'
