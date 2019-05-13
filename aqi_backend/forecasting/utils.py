import os
import copy
import datetime
import numpy as np
import pandas as pd
from django.utils import timezone

from au_epa_data.constants import DATETIME_FORMAT
from au_epa_data.models import Site
from au_epa_data.serializers import GeoSiteSerializer
from au_epa_data.constants import POLLUTANT_TO_MONITOR, DATETIME_FORMAT
from geo_data.models import (
    Fire,
    TrafficFlow,
    TrafficStation
)
from geo_data.serializers import (
    FireSerializer, TrafficStationSerializer
)
from .constants import (
    AU_SITES_FORECAST, SITES_MONITORS, AQ_DATA_DIR, TRAFFIC_FORECAST_STATIONS,
    TRAFFIC_STATIONS
)


def get_datetime_span_dict(start_date, end_date, empty_type=[]):
    span_dict = {}
    print(start_date, end_date)
    date = timezone.make_aware(start_date, is_dst=False)
    end_date = timezone.make_aware(end_date, is_dst=False)

    while date <= end_date:
        span_dict[date.strftime(DATETIME_FORMAT)] = copy.deepcopy(empty_type)
        date = date + datetime.timedelta(hours=1)
    span_dict[end_date.strftime(DATETIME_FORMAT)] = copy.deepcopy(empty_type)

    return span_dict


def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)

    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def get_time_series(file_name, columns):
    file = os.path.join(AQ_DATA_DIR, file_name)
    index_col = 1
    if columns is not None:
        columns = ['date'] + columns
        index_col = 0
    dataset = pd.read_csv(file, index_col=index_col, usecols=columns)
    if columns is None:
        dataset.drop('No', axis=1, inplace=True)
    # summarize first 5 rows
    print(dataset.head(5))
    return dataset


def get_file_name(site_id, variable_list, extra=''):
    return '_'.join([site_id, '_'.join(variable_list), extra])


def get_mult_by_attr(array, attr, value, extra=lambda d: d):
    # array has to be sorted
    results = []
    in_range = False
    for x in array:
        if extra(x[attr]) == value:
            if not in_range:
                in_range = True
            results.append(x)
        else:
            if in_range:
                break
    return results


def get_experimental_data(
        start_date=datetime.datetime(2017, 1, 1, 0, 0),
        # end_date=datetime.datetime(2017, 1, 31, 23, 0)):
        end_date=datetime.datetime(2018, 12, 31, 23, 0),
        include_fires=False, fire_area_radius=0.2):
    timeline = get_datetime_span_dict(
        start_date, end_date, empty_type={
            'sites': {site: [] for site in AU_SITES_FORECAST},
            'traffic_flows': {tf: 0 for tf in TRAFFIC_STATIONS},
            'fires': []
        }
    )

    sites = Site.objects.filter(
        site_id__in=AU_SITES_FORECAST).prefetch_related('measurements')
    traffic_stations = TrafficStation.objects.all()

    for s in sites:
        site_measurements = s.measurements.filter(
            date_time_start__gte=start_date,
            date_time_start__lte=end_date).values(
                'monitor_id', 'value', 'date_time_start').order_by(
                    'date_time_start')
        for m in site_measurements:
            date_str = timezone.localtime(m['date_time_start']).strftime(
                DATETIME_FORMAT)
            timeline[date_str]['sites'][str(s.site_id)].append({
                POLLUTANT_TO_MONITOR[m['monitor_id']]: m['value']})

        traffic_flows = TrafficFlow.objects.filter(
            nb_scats_site__in=TRAFFIC_FORECAST_STATIONS[str(s.site_id)],
            qt_interval_count__gte=start_date,
            qt_interval_count__lte=end_date).values(
                'nb_scats_site', 'traffic_volume', 'qt_interval_count'
        ).order_by('qt_interval_count')
        for tf in traffic_flows:
            date_str = timezone.localtime(tf['qt_interval_count']).strftime(
                DATETIME_FORMAT)
            timeline[date_str]['traffic_flows'][str(tf['nb_scats_site'])] = (
                tf['traffic_volume'])

        s.set_fire_area_radius(fire_area_radius)
        fires = Fire.objects.filter(
            start_date__gte=start_date,
            start_date__lte=end_date,
            season__in=[2017, 2018],
            geom__intersects=s.fire_area
        )
        for f in fires:
            date_t = datetime.datetime(
                f.start_date.year, f.start_date.month, f.start_date.day, 0, 0)
            stop_date = date_t + datetime.timedelta(days=1)
            while date_t <= stop_date:
                date_str = timezone.make_aware(date_t, is_dst=False).strftime(
                    DATETIME_FORMAT)
                if f.pk not in timeline[date_str]['fires']:
                    timeline[date_str]['fires'].append(f.pk)
                date_t = date_t + datetime.timedelta(hours=1)

    results = {
        'sites': GeoSiteSerializer(sites, many=True).data,
        'traffic_stations': TrafficStationSerializer(
            traffic_stations, many=True).data,
        'timeline': timeline,
    }
    if include_fires:
        results['fires'] = get_sites_fires(
            start_date, end_date, fire_area_radius=fire_area_radius)

    return results


def get_sites_fires(
        start_date=datetime.datetime(2017, 1, 1, 0, 0),
        # end_date=datetime.datetime(2017, 1, 31, 23, 0)):
        end_date=datetime.datetime(2018, 12, 31, 23, 0),
        seasons=[2017, 2018],
        fire_area_radius=0.2):
    sites_fire_areas = []
    for s in Site.objects.filter(site_id__in=AU_SITES_FORECAST):
        s.set_fire_area_radius(fire_area_radius)
        sites_fire_areas.append(s.fire_area)

    fires = Fire.get_fire_intersects_situation(
        sites_fire_areas, start_date, end_date, seasons)
    print(len(fires))
    return FireSerializer(fires, many=True).data
