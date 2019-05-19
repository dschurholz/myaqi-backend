import os
import pandas as pd

from au_epa_data.models import Site, Measurement
from geo_data.models import TrafficFlow, Fire
from .constants import (
    AU_SITES_FORECAST, SITES_MONITORS, AQ_DATA_DIR, TRAFFIC_FORECAST_STATIONS,
    SITES_MONITORS_DATES, FIRES_TITLE_PREFIX)


def run(aq_sites=AU_SITES_FORECAST, pollutants=SITES_MONITORS,
        include_traffic=False, include_fires=False, start_date=None,
        end_date=None):
    sites = Site.objects.filter(site_id__in=aq_sites)
    for s in sites:
        s_id = str(s.site_id)
        aq_attrs = pollutants[s_id]
        if start_date is not None and end_date is not None:
            dates = (start_date, end_date)
        else:
            dates = SITES_MONITORS_DATES[s_id]
        measurements = s.measurements.exclude(time_basis_id__in=[
            '8HR_RAV', '24HR_RAV']).filter(
                monitor_id__in=aq_attrs).order_by('date_time_start')
        data = Measurement.measurements_for_forecast(
            measurements, aq_attrs, dates[0], dates[1])
        if pollutants[s_id] == SITES_MONITORS[s_id]:
            file_name = '{}_ALL_aq_series.csv'
        else:
            file_name = '_'.join([
                '{}', *(pollutants[s_id]), 'aq_series.csv'])

        if include_traffic and TRAFFIC_FORECAST_STATIONS[s_id]:
            traffic_flows = TrafficFlow.traffic_flows_for_forecast(
                TRAFFIC_FORECAST_STATIONS[s_id], dates[0], dates[1]
            )
            for k, v in traffic_flows.items():
                if k not in data.keys():
                    data[k] = v
                if k != 'date':
                    file_name = '_'.join(['{}', file_name.format(k)])

        if include_fires:
            fire_areas = {
                i + 1: area
                for i, area in enumerate(
                    s.get_fire_situations_areas())
            }
            fires = Fire.fires_for_forecast(fire_areas, dates[0], dates[1])
            data[FIRES_TITLE_PREFIX] = fires[FIRES_TITLE_PREFIX]
            file_name = '_'.join(['{}', file_name.format('FIRES')])

        for k, v in data.items():
            print(k, len(v))

        dataset = pd.DataFrame(data=data)
        dataset.index.name = 'No'
        print(dataset.head(5))
        # # save to file
        file_name = file_name.format(s.site_id)
        dataset.to_csv(os.path.join(AQ_DATA_DIR, file_name))

        print('Time series saved to:', os.path.join(AQ_DATA_DIR, file_name))
