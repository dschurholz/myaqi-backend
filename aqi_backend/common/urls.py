from rest_framework import routers
from django.urls import re_path

from .rest_views import (
    AQIOrganizationViewSet,
    Questionnaire
)

router = routers.SimpleRouter()
router.register(r'aqi-scales', AQIOrganizationViewSet)
router.namespace = 'common'

urlpatterns = [
    re_path(
        r'^questionnaire/$', Questionnaire.as_view(), name='questionnaire'
    ),
    *router.urls
]
