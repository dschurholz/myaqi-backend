import requests
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from collections import OrderedDict

from common.filters import ExtendedFilter

from .constants import (
    AU_VIC_URL_MAP
)
from .models import (
    Site,
    Monitor
)
from .serializers import (
    SiteSerializer,
    ExtendedSiteSerializer,
    MonitorSerializer,
    ExtendedMonitorSerializer
)


class SiteViewSet(ExtendedFilter, viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    extended_serializer_class = ExtendedSiteSerializer
    permission_classes = [AllowAny, ]


class MonitorViewSet(ExtendedFilter, viewsets.ModelViewSet):
    queryset = Monitor.objects.all()
    serializer_class = MonitorSerializer
    extended_serializer_class = ExtendedMonitorSerializer
    permission_classes = [AllowAny, ]
    lookup_field = 'slug'


class MeasurementsProxy(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        """
        Return a list of all users.
        """

        url = OrderedDict(AU_VIC_URL_MAP)['measurement']
        headers = {'content-type': 'application/json'}
        r = requests.get(url, params=request.query_params, headers=headers)
        return Response(r.json())
