import requests
import io
import json
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from collections import OrderedDict

from common.filters import ExtendedFilter

from .constants import (
    AU_VIC_URL_MAP,
    VIC_ROADS_LIVE,
    VIC_ROADS_MAPSJS_START,
    FIRES,
    MEASUREMENT
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
    View to return all measurements for an AirWatch sensor station.
    """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        """
        Return a list of all measurements.
        """

        url = OrderedDict(AU_VIC_URL_MAP)[MEASUREMENT]
        headers = {'content-type': 'application/json'}
        r = requests.get(url, params=request.query_params, headers=headers)
        return Response(r.json())


class VicEmergencyProxy(APIView):
    """
    View to return all victoria emergency incidents
    """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        """
        Return a list of all incidents.
        """

        url = OrderedDict(AU_VIC_URL_MAP)[FIRES]
        headers = {'content-type': 'application/json'}
        r = requests.get(url, params=request.query_params, headers=headers)
        return Response(r.json())


class VicRoadsLiveProxy(APIView):
    """
    View to return all traffic incidents on victorian roads.
    """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        """
        Return a list of all incidents.
        """

        url = OrderedDict(AU_VIC_URL_MAP)[VIC_ROADS_LIVE]
        headers = {'content-type': 'application/javascript'}
        r = requests.get(url, params=request.query_params, headers=headers)
        incidents = "{}"
        with io.StringIO(r.text) as f:
            line = f.readline()
            while not line.startswith(VIC_ROADS_MAPSJS_START):
                line = f.readline()
            incidents = line.split(VIC_ROADS_MAPSJS_START)[1][:-2]

        return Response(json.loads(incidents))
