from .models import (
    Site,
    SiteList,
    IncidentSite,
    Monitor,
    EquipmentType,
    TimeBasis,
    MonitorTimeBasis,
    Measurement
)

ENTRIES = 'entries'
ENTRIES_COUNT = 'entries_count'
EQUIPMENT_TYPE = 'equipment_type'
FIRES = 'fires'
FOREIGN_KEY = 'foreign_key'
FOREIGN_KEY_SELF = 'foreign_key_self'
INCIDENT_SITE = 'incident_site'
MANY_2_MANY = 'many_to_many'
MEASUREMENT = 'measurement'
MEASUREMENT_MONITOR_TIME_BASIS = 'measurement_monitor_time_basis'
MONITOR = 'monitor'
MONITORS = 'monitors'
MONITOR_TIME_BASIS = 'monitor_time_basis'
REL_FIELD_NAME = 'rel_field_name'
REL_FIELD_TYPE = 'rel_field_type'
RELATIONAL_TABLE_STRUCTURE = 'relational_table_structure'
SITE = 'site'
SITE_WITH_MEASUREMENTS = 'sites_measurements'
SITE_LIST = 'site_list'
SITES = 'sites'
TABLE_STRUCTURE = 'table_structure'
TIME_BASIS = 'time_basis'
UNIQUE_PARAMS = 'unique_params'
VIC_ROADS_LIVE = 'vic_roads_live'

AU_VIC_URL_MAP = (
    (MONITOR, 'http://sciwebsvc.epa.vic.gov.au/aqapi/Monitors'),
    (SITE, 'http://sciwebsvc.epa.vic.gov.au/aqapi/Sites'),
    (TIME_BASIS, 'http://sciwebsvc.epa.vic.gov.au/aqapi/Timebasis'),
    (MEASUREMENT, 'http://sciwebsvc.epa.vic.gov.au/aqapi/Measurements'),
    (FIRES, 'http://emergency.vic.gov.au/public/osom-geojson.json'),
    (VIC_ROADS_LIVE, 'https://traffic.vicroads.vic.gov.au/maps.js'),
    (SITE_WITH_MEASUREMENTS, 'http://sciwebsvc.epa.vic.gov.au/aqapi/SitesHourlyAirQuality?dateTimeStart={0}')
)

COMMAND_MODEL_MAP = (
    (SITE, Site),
    (INCIDENT_SITE, IncidentSite),
    (SITE_LIST, SiteList),
    (MONITOR, Monitor),
    (EQUIPMENT_TYPE, EquipmentType),
    (TIME_BASIS, TimeBasis),
    (MONITOR_TIME_BASIS, MonitorTimeBasis),
    (MEASUREMENT_MONITOR_TIME_BASIS, MonitorTimeBasis),
    (MEASUREMENT, Measurement)
)

SITE_LIST_TABLE_FIELD_MAP = (
    ('Name', 'name'),
)

INCIDENT_SITE_TABLE_FIELD_MAP = (
    ('EMVUrl', 'emv_url'),
    ('IncidentIcon', 'incident_icon'),
)

# Map(Name in the XML/JSON, Name in the database)
SITE_TABLE_FIELD_MAP = (
    ('SiteId', 'site_id'),
    ('Name', 'name'),
    ('Latitude', 'latitude'),
    ('Longitude', 'longitude'),
    ('FireHazardCategory', 'fire_hazard_category'),
    ('IsStationOffline', 'is_station_offline'),
    ('HasIncident', 'has_incident'),
    ('IncidentType', 'incident_type'),
)

SITE_TABLE_RELATIONAL_FIELD_MAP = (
    ('SiteList', SITE_LIST),
    ('IncidentSite', INCIDENT_SITE),
)

SITE_SERVICE_METADATA = (
    (ENTRIES_COUNT, 'NumberOfSites'),
    (ENTRIES, 'Sites'),
    (TABLE_STRUCTURE, SITE_TABLE_FIELD_MAP),
    (RELATIONAL_TABLE_STRUCTURE, SITE_TABLE_RELATIONAL_FIELD_MAP),
    (UNIQUE_PARAMS, ['SiteId'])
)

INCIDENT_SITE_SERVICE_METADATA = (
    (TABLE_STRUCTURE, INCIDENT_SITE_TABLE_FIELD_MAP),
    (REL_FIELD_TYPE, FOREIGN_KEY),
    (REL_FIELD_NAME, 'site')
)

SITE_LIST_SERVICE_METADATA = (
    (TABLE_STRUCTURE, SITE_LIST_TABLE_FIELD_MAP),
    (REL_FIELD_TYPE, MANY_2_MANY)
)

EQUIPMENT_TYPE_TABLE_FIELD_MAP = (
    ('IdNumber', 'id_number'),
    ('Code', 'code'),
    ('Description', 'description'),
)

MONITOR_TABLE_FIELD_MAP = (
    ('MonitorId', 'monitor_id'),
    ('ShortName', 'short_name'),
    ('CommonName', 'common_name'),
    ('EPADescriptionURL', 'epa_description_url'),
    ('UnitOfMeasure', 'unit_of_measure'),
    ('PresentationPrecision', 'presentation_precision'),
)

MONITOR_TABLE_RELATIONAL_FIELD_MAP = (
    ('EquipmentType', EQUIPMENT_TYPE),
    ('SiteId', SITES),
)

MONITOR_SERVICE_METADATA = (
    (ENTRIES_COUNT, 'NumberOfMonitors'),
    (ENTRIES, 'Monitors'),
    (TABLE_STRUCTURE, MONITOR_TABLE_FIELD_MAP),
    (RELATIONAL_TABLE_STRUCTURE, MONITOR_TABLE_RELATIONAL_FIELD_MAP),
    (UNIQUE_PARAMS, ['MonitorId'])
)

EQUIPMENT_TYPE_SERVICE_METADATA = (
    (TABLE_STRUCTURE, EQUIPMENT_TYPE_TABLE_FIELD_MAP),
    (REL_FIELD_TYPE, FOREIGN_KEY_SELF),
    (REL_FIELD_NAME, EQUIPMENT_TYPE)
)

SITES_REL_SERVICE_METADATA = (
    (TABLE_STRUCTURE, None),
    (REL_FIELD_TYPE, MANY_2_MANY),
    (REL_FIELD_NAME, 'site_id')
)

TIME_BASIS_TABLE_FIELD_MAP = (
    ('TimeBaseId', 'time_base_id'),
    ('Description', 'description'),
    ('IsRollingAverage', 'is_rolling_average'),
    ('RollingAveragePeriod', 'rolling_average_period'),
    ('MinDataPercent', 'min_data_percent'),
    ('TimeBasisDescURL', 'time_basis_desc_url'),
)

TIME_BASIS_TABLE_RELATIONAL_FIELD_MAP = (
    ('SiteId', SITES),
    ('MonitorTimeBasis', MONITOR_TIME_BASIS)
)

TIME_BASIS_SERVICE_METADATA = (
    (ENTRIES_COUNT, 'NumberOfTimeBasis'),
    (ENTRIES, 'TimeBasis'),
    (TABLE_STRUCTURE, TIME_BASIS_TABLE_FIELD_MAP),
    (RELATIONAL_TABLE_STRUCTURE, TIME_BASIS_TABLE_RELATIONAL_FIELD_MAP),
    (UNIQUE_PARAMS, ['TimeBaseId'])
)

MONITOR_TIME_BASIS_TABLE_FIELD_MAP = (
    ('AQIPollutantStandard', 'aqi_pollutant_standard'),
    ('IncidentType', 'incident_type'),
    ('PresentationOrder', 'presentation_order'),
    ('CalcAQI', 'calc_aqi'),
    ('CalcHealthCategory', 'calc_health_category'),
    ('MonitorId', 'monitor_id'),
)

MONITOR_TIME_BASIS_SERVICE_METADATA = (
    (TABLE_STRUCTURE, MONITOR_TIME_BASIS_TABLE_FIELD_MAP),
    (REL_FIELD_TYPE, FOREIGN_KEY),
    (REL_FIELD_NAME, TIME_BASIS)
)

MEASUREMENT_TABLE_FIELD_MAP = (
    ('DateTimeStart', 'date_time_start'),
    ('DateTimeRecorded', 'date_time_recorded'),
    ('Value', 'value'),
    ('QualityStatus', 'quality_status'),
    ('AQIIndex', 'aqi_index'),
    ('AQICategoryAbbreviation', 'aqi_category_threshold_id'),
    ('HealthCategoryLevel', 'health_category_threshold_id'),
    ('SiteId', 'site_id'),
    ('TimeBaseId', 'time_basis_id'),
    ('MonitorId', 'monitor_id'),
)

MEASUREMENT_TABLE_RELATIONAL_FIELD_MAP = (
    ('EquipmentType', EQUIPMENT_TYPE),
    ('MonitorTimeBasis', MEASUREMENT_MONITOR_TIME_BASIS)
)

MEASUREMENT_SERVICE_METADATA = (
    (ENTRIES_COUNT, 'NumberOfMeasurements'),
    (ENTRIES, 'Measurements'),
    (TABLE_STRUCTURE, MEASUREMENT_TABLE_FIELD_MAP),
    (RELATIONAL_TABLE_STRUCTURE, MEASUREMENT_TABLE_RELATIONAL_FIELD_MAP),
    (UNIQUE_PARAMS, ['DateTimeStart', 'SiteId', 'MonitorId', 'TimeBaseId'])
)

MEASUREMENT_MONITOR_TIME_BASIS_SERVICE_METADATA = (
    (TABLE_STRUCTURE, MONITOR_TIME_BASIS_TABLE_FIELD_MAP),
    (REL_FIELD_TYPE, FOREIGN_KEY_SELF),
    (REL_FIELD_NAME, MONITOR_TIME_BASIS)
)

SERVICES_METADATA = (
    (SITE, SITE_SERVICE_METADATA),
    (INCIDENT_SITE, INCIDENT_SITE_SERVICE_METADATA),
    (SITE_LIST, SITE_LIST_SERVICE_METADATA),
    (SITES, SITES_REL_SERVICE_METADATA),
    (MONITOR, MONITOR_SERVICE_METADATA),
    (EQUIPMENT_TYPE, EQUIPMENT_TYPE_SERVICE_METADATA),
    (TIME_BASIS, TIME_BASIS_SERVICE_METADATA),
    (MONITOR_TIME_BASIS, MONITOR_TIME_BASIS_SERVICE_METADATA),
    (MEASUREMENT, MEASUREMENT_SERVICE_METADATA),
    (MEASUREMENT_MONITOR_TIME_BASIS,
        MEASUREMENT_MONITOR_TIME_BASIS_SERVICE_METADATA)
)

VIC_ROADS_MAPSJS_START = 'var preload_data = '
