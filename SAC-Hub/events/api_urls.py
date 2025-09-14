from rest_framework import routers
from .views import EventViewSet, CollaborationRequestViewSet

router = routers.DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'collaboration-requests', CollaborationRequestViewSet)

urlpatterns = router.urls
