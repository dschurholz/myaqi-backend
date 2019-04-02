from django.urls import re_path
from rest_framework import routers

from .rest_views import UserViewSet, current_user_view

router = routers.SimpleRouter()
router.register(r'accounts', UserViewSet)
router.namespace = 'accounts'

urlpatterns = router.urls + [
    re_path(r'^me/', current_user_view, name="me"),
]
