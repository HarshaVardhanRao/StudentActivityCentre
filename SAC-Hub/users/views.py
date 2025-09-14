
from rest_framework import viewsets
from .models import User, Club, Department, Notification
from .serializers import UserSerializer, ClubSerializer, DepartmentSerializer, NotificationSerializer

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer

class ClubViewSet(viewsets.ModelViewSet):
	queryset = Club.objects.all()
	serializer_class = ClubSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
	queryset = Department.objects.all()
	serializer_class = DepartmentSerializer

class NotificationViewSet(viewsets.ModelViewSet):
	queryset = Notification.objects.all()
	serializer_class = NotificationSerializer
