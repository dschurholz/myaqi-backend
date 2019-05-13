import datetime
import requests
import copy
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from collections import OrderedDict

from au_epa_data.constants import AU_VIC_URL_MAP, WEATHERBIT_FORECAST

from .utils import get_experimental_data, get_sites_fires


class ExperimentsMapDataView(APIView):
    """
    View to return the data for the forecasting experiments to be rendered
    at the MyAQI frontend map.
    """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        """
        Return experiments in chronological order.
        """
        start_date_str = request.GET.get('start_date', '2017010100')
        end_date_str = request.GET.get('end_date', '2019010100')
        start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d%H')
        end_date = datetime.datetime.strptime(end_date_str, '%Y%m%d%H')

        experimental_data = get_experimental_data(start_date, end_date)

        return Response(experimental_data)


class FiresExperimentsDataView(APIView):
    """
    View to return the fires for the forecasting experiments to be rendered
    at the MyAQI frontend map.
    """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        """
        Return fires in chronological order.
        """
        start_date_str = request.GET.get('start_date', '2017010100')
        end_date_str = request.GET.get('end_date', '2019010100')
        start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d%H')
        end_date = datetime.datetime.strptime(end_date_str, '%Y%m%d%H')

        fires = get_sites_fires(start_date, end_date)
        return Response(fires)


class WeatherbitForecastProxy(APIView):
    """
    View to return all measurements for an AirWatch sensor station.
    """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        """
        Return a list of all measurements.
        """

        url = OrderedDict(AU_VIC_URL_MAP)[WEATHERBIT_FORECAST]
        headers = {'content-type': 'application/json'}

        params = copy.copy(request.query_params)
        params['key'] = settings.WEATHER_BIT_API_KEY
        r = requests.get(url, params=params, headers=headers)
        return Response(r.json())
