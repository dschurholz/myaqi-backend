import os
import json
import copy
import datetime
import numpy as np
import pandas as pd
from django.utils import timezone

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
    AU_SITES_FORECAST, AQ_DATA_DIR, TRAFFIC_FORECAST_STATIONS,
    TRAFFIC_STATIONS, HISTORICAL_DATA_FILE, FIRE_SEVERITIES
)


def get_datetime_span_dict(start_date, end_date, empty_type=[]):
    """Returns a dictionary of dates spanning between start_date and end_date.
    The keys are the datestrings and the empty_type will be the value.

    :param start_date: date and time from where to start the range.
    :type start_date: datetime.datetime
    :param end_date: date and time on which to stop the range.
    :type end_date: datetime.datetime
    :param empty_type: default value for each key in the range. 
    :type empty_type: any
    :rtype: dict
    
    """
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
    """Returns the MAPE error of a ground truth vs. predicted values array.

    :param y_true: ground truth of a pollutant values.
    :type y_true: numpy.array
    :param y_pred: predicted values for a pollutant.
    :type y_pred: numpy.array
    :rtype: float

    """
    y_true, y_pred = np.array(y_true), np.array(y_pred)

    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def get_time_series(file_name, columns=None, file_dir=None):
    """Load a pollutant levels timeseries dataset from a .csv file.

    :param file_name: CSV file from which to load the dataset values.
    :type file_name: string
    :param columns: a list of column names from the CSV file to load.
    :type columns: string[]
    :param file_dir: if the file to load is not in ./data/air_quality
    :type file_dir: string
    :rtype: pandas.DataFrame

    """
    file = os.path.join(
        AQ_DATA_DIR if file_dir is None else file_dir, file_name)
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
    """Create a file name for a forecast made with a given set of variables.

    :param site_id: AQ monitoring station site id.
    :type site_id: string or int
    :param variable_list: a list of the variables used for the prediction.
    :type variable_list: string[]
    :param extra: any extra information to add to the file name.
    :type extra: string
    :rtype: string

    """
    return '_'.join([site_id, '_'.join(variable_list), extra])


def get_mult_by_attr(array, attr, value, extra=lambda d: d):
    """
    Helper function to get objects with the same attribute value from an array.
    
    .. note:: *array* has to be sorted
    """
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
        end_date=datetime.datetime(2018, 12, 31, 23, 0),
        include_fires=False, save_file=False):
    """Generate the dictionary with experimental data ready to be loaded and 
    run with the forecasting module.

    :param start_date: date and time from where to start retrieving the data.
    :type start_date: datetime.datetime
    :param end_date: date and time on which to stop retrieving the data.
    :type end_date: datetime.datetime
    :param include_fires: if to add information regarding the fire incidents.
    :type include_fires: boolean
    :param save_file: if to save the resulting dict into a file.
    :type save_file: boolean
    :rtype: dict

    Result dict:
        The resulting dict has 3 to 4 keys (depending if *include_fires* is
        `true`). Example::
            {
                'sites': [{site1...}, {site2...}, ...],
                'traffic_stations': [{traffic_station1...}, {traffic_station2...}, ...],
                'timeline': {date1: [pol1, pol2, ...], date2: [pol1, pol2, ...], ...},
                'fires': [fire1, fire2, ...]
            }

    """

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

        s.set_fire_area_radius()
        fires = Fire.objects.filter(
            start_date__gte=start_date,
            start_date__lte=end_date,
            season__in=[2017, 2018],
            geom__intersects=s.fire_area
        )
        for f in fires:
            date_t = datetime.datetime(
                f.start_date.year, f.start_date.month, f.start_date.day, 0, 0)
            stop_date = date_t + datetime.timedelta(
                days=FIRE_SEVERITIES[f.fire_svrty])
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
        results['fires'] = get_sites_fires(start_date, end_date)

    if save_file:
        with open(HISTORICAL_DATA_FILE, 'w') as f:
            f.write(json.dumps(results))
    return results


def get_sites_fires(
        start_date=datetime.datetime(2017, 1, 1, 0, 0),
        end_date=datetime.datetime(2018, 12, 31, 23, 0),
        seasons=[2017, 2018]):
    """Generate a list of fire incidents that affect the AQ monitoring stations
    in the AU_SITES_FORECAST list.

    :param start_date: date and time from where to start retrieving the data.
    :type start_date: datetime.datetime
    :param end_date: date and time on which to stop retrieving the data.
    :type end_date: datetime.datetime
    :param seasons: the years from which to consider the fires (because
        incidents of previous years may span over the entered date range).
    :type seasons: int[]
    :rtype: Fire[]

    """
    sites_fire_areas = []
    for s in Site.objects.filter(site_id__in=AU_SITES_FORECAST):
        s.set_fire_area_radius()
        sites_fire_areas.append(s.fire_area)

    fires = Fire.get_fire_intersects_situation(
        sites_fire_areas, start_date, end_date, seasons)
    return FireSerializer(fires, many=True).data
