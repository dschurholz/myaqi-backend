from django.urls import re_path
from rest_framework import routers

from .rest_views import (
    MeasurementsProxy,
    MonitorViewSet,
    SitesProxy,
    SiteViewSet,
    VicEmergencyProxy,
    VicRoadsLiveProxy
)

router = routers.SimpleRouter()
router.register(r'sites', SiteViewSet)
router.register(r'monitors', MonitorViewSet)
router.namespace = 'au-epa-data'

urlpatterns = [
    re_path(
        'measurements', MeasurementsProxy.as_view(), name='measurements-proxy'
    ),
    re_path(
        r'^fires', VicEmergencyProxy.as_view(), name='fires-proxy'
    ),
    re_path(
        r'^traffic$', VicRoadsLiveProxy.as_view(), name='traffic-proxy'
    ),
    re_path(
        'sites-live', SitesProxy.as_view(), name='sites-proxy'
    ),
    *router.urls
]
