from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Fire, TrafficFlow
from .serializers import FireSerializer, TrafficFlowSerializer


class FireViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Use this endpoint to retrieve fires.
    """
    queryset = Fire.objects.all()
    serializer_class = FireSerializer
    permission_classes = [AllowAny]
    filter_fields = ('season', 'start_date', )


class TrafficFlowViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Use this endpoint to retrieve traffic flows.
    """
    queryset = TrafficFlow.objects.all()
    serializer_class = TrafficFlowSerializer
    permission_classes = [AllowAny]
    filter_fields = ('nb_scats_site', )
