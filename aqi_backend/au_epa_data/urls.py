from rest_framework import routers

from .rest_views import (
    SiteViewSet,
    MonitorViewSet
)

router = routers.SimpleRouter()
router.register(r'sites', SiteViewSet)
router.register(r'monitors', MonitorViewSet)
router.namespace = 'au-epa-data'

urlpatterns = router.urls
