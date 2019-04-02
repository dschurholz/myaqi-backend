from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import (
    AQIOrganization
)
from .serializers import (
    AQIOrganizationSerializer
)


class AQIOrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AQIOrganization.objects.all()
    serializer_class = AQIOrganizationSerializer
    permission_classes = [AllowAny, ]
