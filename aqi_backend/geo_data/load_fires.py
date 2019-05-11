import os
from django.contrib.gis.utils import LayerMapping

from .models import Fire
from.constants import FIRE_MAPPING

fires_shp = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 'data', 'fire', 'layer',
        'fire_history.shp'),
)


def run(verbose=True):
    lm = LayerMapping(Fire, fires_shp, FIRE_MAPPING, transform=False)
    lm.save(strict=True, verbose=verbose)
