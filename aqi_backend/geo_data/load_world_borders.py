import os
from django.contrib.gis.utils import LayerMapping

from .models import WorldBorder
from .constants import WORLD_MAPPING

world_shp = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 'data', 'world',
        'TM_WORLD_BORDERS-0.3.shp'),
)


def run(verbose=True):
    lm = LayerMapping(WorldBorder, world_shp, WORLD_MAPPING, transform=False)
    lm.save(strict=True, verbose=verbose)
