

FIRE_MAPPING = {
    'firetype': 'FIRETYPE',
    'season': 'SEASON',
    'fire_no': 'FIRE_NO',
    'name': 'NAME',
    'start_date': 'START_DATE',
    'strtdatit': 'STRTDATIT',
    'treat_type': 'TREAT_TYPE',
    'fire_svrty': 'FIRE_SVRTY',
    'fire_cover': 'FIRE_COVER',
    'firekey': 'FIREKEY',
    'cr_date': 'CR_DATE',
    'updatedate': 'UPDATEDATE',
    'area_ha': 'AREA_HA',
    'method': 'METHOD',
    'methd_cmnt': 'METHD_CMNT',
    'accuracy': 'ACCURACY',
    'dse_id': 'DSE_ID',
    'cfa_id': 'CFA_ID',
    'districtid': 'DISTRICTID',
    'geom': 'MULTIPOLYGON',
}

WORLD_MAPPING = {
    'fips': 'FIPS',
    'iso2': 'ISO2',
    'iso3': 'ISO3',
    'un': 'UN',
    'name': 'NAME',
    'area': 'AREA',
    'pop2005': 'POP2005',
    'region': 'REGION',
    'subregion': 'SUBREGION',
    'lon': 'LON',
    'lat': 'LAT',
    'mpoly': 'MULTIPOLYGON',
}

TRAFFIC_NB_SCATS_SITE = 'NB_SCATS_SITE'
TRAFFIC_NM_REGION = 'NM_REGION'
TRAFFIC_FLOW_DATE = 'QT_INTERVAL_COUNT'
TRAFFIC_NB_DETECTOR = 'NB_DETECTOR'
TRAFFIC_CT_RECORDS = 'CT_RECORDS'
TRAFFIC_FLOW_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
TRAFFIC_FLOW_VOLUME = 'traffic_volume'

TRAFFIC_RELEVANT_STATIONS = [
    # MOOROOLBARK
    '118',
    # ALPHINGTON
    # '4653',
    # # MELBOURNE CBD,
    # '4405', '4406', '4419', '4404',
    # TRARALGON
    # No Measurement nearby
]

TRAFFIC_FLOW_FIELD_MAPPING = {
    TRAFFIC_NB_SCATS_SITE: 'nb_scats_site',
    TRAFFIC_FLOW_DATE: 'qt_interval_count',
    TRAFFIC_NB_DETECTOR: 'nb_detector',
    TRAFFIC_NM_REGION: 'region_name',
    TRAFFIC_CT_RECORDS: 'records_count',
}

TRAFFIC_FLOW_TEMPLATE = {
    'nb_scats_site': None,
    'qt_interval_count': None,
    'region_name': None,
    'records_count': 96,
    TRAFFIC_FLOW_VOLUME: 0
}
