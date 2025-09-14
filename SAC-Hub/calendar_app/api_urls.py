from rest_framework import routers
from .views import CalendarEntryViewSet

router = routers.DefaultRouter()
router.register(r'calendar-entries', CalendarEntryViewSet)

urlpatterns = router.urls
