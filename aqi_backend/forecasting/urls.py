from django.urls import re_path

from .rest_views import (
    ExperimentsMapDataView,
    FiresExperimentsDataView
)

urlpatterns = [
    re_path(
        r'^experiments/map-data$', ExperimentsMapDataView.as_view(),
        name='experiments-map-data'
    ),
    re_path(
        r'^experiments/fires-data$', FiresExperimentsDataView.as_view(),
        name='experiments-fire-data'
    ),
]
