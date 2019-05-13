from rest_framework import routers

from .rest_views import (
    FireViewSet,
    TrafficFlowViewSet
)

router = routers.SimpleRouter()
router.register(r'historic-fires', FireViewSet)
router.register(r'traffic-flows', TrafficFlowViewSet)
router.namespace = 'geo_data'

urlpatterns = router.urls
