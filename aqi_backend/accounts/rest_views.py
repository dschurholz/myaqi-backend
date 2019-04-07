import logging
from django.contrib.auth import get_user_model

from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from .serializers import (UserSerializer, ExtendedUserSerializer, UserProfileQuestionnaireAnswerSerializer)

UserModel = get_user_model()

logger = logging.getLogger('myaqi')


class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    filter_fields = ('email', )

    def get_permissions(self):
        return ([AllowAny()] if self.request.method == 'POST' else
                [IsAdminUser()])


class CurrentUserView(generics.RetrieveUpdateDestroyAPIView):
    """
    Use this endpoint to retrieve/update user.
    """
    model = UserModel
    serializer_class = ExtendedUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, *args, **kwargs):
        return self.request.user


current_user_view = CurrentUserView.as_view()
