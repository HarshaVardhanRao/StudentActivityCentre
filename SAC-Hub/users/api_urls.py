from rest_framework import routers
from users.views import UserViewSet, ClubViewSet, DepartmentViewSet, NotificationViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'clubs', ClubViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = router.urls
