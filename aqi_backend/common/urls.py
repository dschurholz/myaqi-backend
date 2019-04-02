from rest_framework import routers

from .rest_views import (
    AQIOrganizationViewSet,
)

router = routers.SimpleRouter()
router.register(r'aqi-scales', AQIOrganizationViewSet)
router.namespace = 'common'

urlpatterns = router.urls
