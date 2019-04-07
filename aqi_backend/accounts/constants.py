AU_EPA_AQI = 'au'
EU_EEA_AQI = 'eu'
USA_EPA_AQI = 'us'

AQI_SCALES = (
    (AU_EPA_AQI, 'Australian EPA AQI'),
    (EU_EEA_AQI, 'EU EEA AQI'),
    (USA_EPA_AQI, 'USA EPA AQI')
)

# Sensitivity levels 0-neutral, 1-low, 2-moderate, 3-high, 4-extremely high
SENSITIVITY_LEVELS_IDS = {
    'NEUTRAL': 0,
    'LOW': 1,
    'MODERATE': 2,
    'HIGH': 3,
    'EXTREMELY_HIGH': 4
}

SENSITIVITY_LEVELS = (
    (SENSITIVITY_LEVELS_IDS['NEUTRAL'], 'Neutral'),
    (SENSITIVITY_LEVELS_IDS['LOW'], 'Low'),
    (SENSITIVITY_LEVELS_IDS['MODERATE'], 'Moderate'),
    (SENSITIVITY_LEVELS_IDS['HIGH'], 'High'),
    (SENSITIVITY_LEVELS_IDS['EXTREMELY_HIGH'], 'Extremeley high')
)

TEMP_POLLUTANT_TRANSLATION = {
    'so2': 'no2',
    'pm10': 'pm2.5',
    'co': 'pm2.5',
    'pm2.5': 'pm2.5',
    'no2': 'no2',
    'o3': 'o3',
}
