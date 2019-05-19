import os
import datetime

AQ_DATA_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 'data', 'air_quality'),
)

TRAFFIC_DATA_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 'data', 'traffic'),
)

FIRES_DATA_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 'data', 'fires'),
)

FIGS_DATA_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 'data', 'figs'),
)

MODELS_DATA_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 'data', 'models'),
)

HISTORICAL_DATA_FILE = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 'data', 'json',
        'historic_overall_data_2017_2018.json'),
)

AU_SITES_FORECAST = ['10001', '10011', '10239', '10136']

DATES = [
    ['2016123123', '2017020100'],
    ['2017020100', '2017030100'],
    ['2017030100', '2017040100'],
    ['2017040100', '2017050100'],
    ['2017050100', '2017060100'],
    ['2017060100', '2017070100'],
    ['2017070100', '2017080100'],
    ['2017080100', '2017090100'],
    ['2017090100', '2017100100'],
    ['2017100100', '2017110100'],
    ['2017110100', '2017120100'],
    ['2017120100', '2018010100'],
    ['2018010100', '2018020100'],
    ['2018020100', '2018030100'],
    ['2018030100', '2018040100'],
    ['2018040100', '2018050100'],
    ['2018050100', '2018060100'],
    ['2018060100', '2018070100'],
    ['2018070100', '2018080100'],
    ['2018080100', '2018090100'],
    ['2018090100', '2018100100'],
    ['2018100100', '2018110100'],
    ['2018110100', '2018120100'],
    ['2018120100', '2019010100'],
]


SITES_MONITORS = {
    # Alphington
    '10001': [
        'sp_AQI', 'BPM2.5', 'O3', 'NO2', 'SO2', 'PM10', 'CO',
        'DBT', 'VWS', 'VWD'],
    # Melbourne CDB
    '10239': ['sp_AQI', 'BPM2.5'],
    # Mooroolbark
    '10136': ['sp_AQI', 'iPM2.5', 'O3', 'PM10', 'DBT', 'VWS', 'VWD'],
    # Traralgon
    '10011': [
        'sp_AQI', 'BPM2.5', 'O3', 'NO2', 'SO2', 'PM10', 'CO', 'DBT', 'VWS',
        'VWD'],
}

SITES_MONITORS_DATES = {
    '10001': (
        datetime.datetime(2017, 1, 1, 0, 0),
        datetime.datetime(2018, 12, 31, 23, 0),
    ),
    # Melbourne CDB
    '10239': (
        datetime.datetime(2017, 5, 9, 14, 0),
        datetime.datetime(2018, 12, 31, 23, 0),
    ),
    # Mooroolbark
    '10136': (
        datetime.datetime(2017, 1, 1, 0, 0),
        datetime.datetime(2018, 12, 31, 23, 0),
    ),
    # Traralgon
    '10011': (
        datetime.datetime(2017, 1, 1, 0, 0),
        datetime.datetime(2018, 12, 31, 23, 0),
    ),
}

TIME_BASIS = {
    'sp_AQI': ['1HR_AV'],
    'BPM2.5': ['1HR_AV', '24HR_RAV'],
    'iPM2.5': ['1HR_AV', '24HR_RAV'],
    'O3': ['1HR_AV'],
    'NO2': ['1HR_AV'],
    'SO2': ['1HR_AV'],
    'PM10': ['1HR_AV'],
    'CO': ['1HR_AV', '8HR_RAV'],
    'DBT': [None],
    'VWD': [None],
    'VWS': [None],
}

TRAFFIC_FLOW_TITLE_PREFIX = 'TRAFFIC'

TRAFFIC_STATIONS = ['118', '4653', '4419']

TRAFFIC_FORECAST_STATIONS = {
    # MOOROOLBARK
    '10136': ['118'],
    # ALPHINGTON
    '10001': ['4653'],
    # MELBOURNE CBD,
    '10239': ['4419', '4405', '4406', '4404'],
    # TRARALGON
    # No Measurement nearby
    '10011': []
}

FORECASTABLE_POLLUTANTS = ['AQI', 'PM2.5', 'PM10', 'O3', 'NO2', 'SO2', 'CO']

# Number of days to account for the fire
FIRE_SEVERITIES = {
    'BURNT_1': 3,
    'BURNT_2': 5,
    'BURNT_2F': 5,
    'BURNT_2P': 5,
    'BURNT_3': 10,
    'BURNT_4': 15,
    'BURNT_FOREST': 15,
    'BURNT_NONFOREST': 10,
    'BURNT_UNKNOWN': 3,
    'UNBURNT': 3
}

FSITUATION_VERY_LOW = 1
FSITUATION_LOW = 2
FSITUATION_MODERATE = 3
FSITUATION_HIGH = 4
FSITUATION_EXTREMELY_HIGH = 5
FIRE_SITUATIONS_RADIUS = {
    FSITUATION_VERY_LOW: 1,
    FSITUATION_LOW: 0.8,
    FSITUATION_MODERATE: 0.6,
    FSITUATION_HIGH: 0.4,
    FSITUATION_EXTREMELY_HIGH: 0.2
}

FIRES_TITLE_PREFIX = 'FIRES'

# Fire incidents distance to station for it to be relevant (in metres)
FIRE_SITUATION_STATION_RADIUS = {
    # ALPHINGTON (in city)
    '10001': 20 * 1000,
    # MELBOURNE CBD (in city centre)
    '10239': 20 * 1000,
    # MOOROOLBARK (outside city)
    '10136': 100 * 1000,
    # TRARALGON (countryside)
    '10011': 100 * 1000
}
