from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import (
    AQIOrganization,
    ProfileQuestion
)
from .serializers import (
    AQIOrganizationSerializer,
    ProfileQuestionSerializer
)


class AQIOrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AQIOrganization.objects.all()
    serializer_class = AQIOrganizationSerializer
    permission_classes = [AllowAny, ]


class Questionnaire(APIView):
    """
    View to return the Profile AQI Incidense Questionnaire
    """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        questions = ProfileQuestion.objects.filter(active=True)
        serializer = ProfileQuestionSerializer(questions, many=True)
        return Response(serializer.data)
