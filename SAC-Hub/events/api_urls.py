from rest_framework import routers
from .views import EventViewSet, CollaborationRequestViewSet, EventReportViewSet

router = routers.DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'collaboration-requests', CollaborationRequestViewSet)
router.register(r'event-reports', EventReportViewSet)

urlpatterns = router.urls
