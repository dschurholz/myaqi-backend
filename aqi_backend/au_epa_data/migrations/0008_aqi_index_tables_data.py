# Generated by Django 2.1.5 on 2019-02-19 05:51

from django.db import migrations

AQI_CATEGORY_THRESHOLDS = [
    {
        "abbreviation": "VG",
        "lower_threshold_value": -5.0,
        "upper_threshold_value": 33.99,
        "description": "Very Good",
        "background_colour": "#339966",
        "foreground_colour": "#000000"
    }, {
        "abbreviation": "G",
        "lower_threshold_value": 34.0,
        "upper_threshold_value": 66.99,
        "description": "Good",
        "background_colour": "#3399FF",
        "foreground_colour": "#000000"
    }, {
        "abbreviation": "F",
        "lower_threshold_value": 67.0,
        "upper_threshold_value": 99.99,
        "description": "Fair",
        "background_colour": "#FFFF00",
        "foreground_colour": "#000000"
    }, {
        "abbreviation": "P",
        "lower_threshold_value": 100.0,
        "upper_threshold_value": 149.99,
        "description": "Poor",
        "background_colour": "#FF0000",
        "foreground_colour": "#000000"
    }, {
        "abbreviation": "VP",
        "lower_threshold_value": 150.0,
        "upper_threshold_value": 99999.0,
        "description": "Very Poor",
        "background_colour": "#000000",
        "foreground_colour": "#FFFFFF"
    }, {
        "abbreviation": "NA",
        "lower_threshold_value": None,
        "upper_threshold_value": None,
        "description": "Not Available",
        "background_colour": "#999999",
        "foreground_colour": "#999999"
    }, {
        "abbreviation": "EC",
        "lower_threshold_value": None,
        "upper_threshold_value": None,
        "description": "Empty cell",
        "background_colour": "#CCCCCC",
        "foreground_colour": "#CCCCCC"
    }
]

HEALTH_CATEGORY_THRESHOLD = [
    {
        'level': 0,
        'threshold_value': None,
        'description': 'Unavailable',
        'value_range': None,
        'visibility': None,
        'message': '',
        'background_colour': None,
        'foreground_colour': None
    }, {
        'level': 1,
        'threshold_value': 8.99,
        'description': 'LOW',
        'value_range': '0.0-8.9',
        'visibility': 'More than 20 km',
        'message': '<p>Over the last 24 hours, the average level of PM2.5 particles in the air has met the &#39;low&#39; health category. This means that the level of PM2.5 particles in the air can be considered healthy for everyone.<br />\r\n<br />\r\nThis health category is based on the 24-hour rolling average only.<br />\r\n<br />\r\nThere is no cautionary advice for this health category.<br />\r\n<br />\r\n<strong>For information, updates and advice relating to incidents affecting air quality in this area please go to: <a href="http://emergency.vic.gov.au/respond/">http://emergency.vic.gov.au/respond/</a></strong></p>',
        'background_colour': '#70930',
        'foreground_colour': '#FFFFFF'
    }, {
        'level': 3,
        'threshold_value': 39.99,
        'description': 'Unhealthy for sensitive groups',
        'value_range': '26.0-39.9',
        'visibility': '5 - 10 km',
        'message': '<p>People over 65, children 14 years and younger, pregnant women and those with existing heart or lung conditions should&nbsp;<strong>reduce</strong>&nbsp;prolonged or heavy physical activity. Where possible, these people should also limit the time spent outdoors.</p>\r\n\r\n<p>Anyone with a heart or lung condition should take their medication as prescribed by their doctor.</p>\r\n\r\n<p>People with asthma should follow their asthma management plan.</p>\r\n\r\n<p>Anyone with concerns about their health should seek medical advice or call NURSE-ON-CALL on&nbsp;<a href="tel:1300606024">1300 60 60 24</a>.</p>\r\n\r\n<p><strong>For further information, updates and advice relating to incidents affecting air quality in this area, please go to&nbsp;<a href="http://emergency.vic.gov.au/respond">http://emergency.vic.gov.au/respond</a></strong></p>',
        'background_colour': '#EAAF0F',
        'foreground_colour': '#FFFFFF'
    }, {
        'level': 4,
        'threshold_value': 106.99,
        'description': 'Unhealthy all',
        'value_range': '40-106.9',
        'visibility': '2 - 5 km',
        'message': '<p>Excessive smoke levels can not only aggravate existing heart or lung conditions, but may also cause members of the community to experience irritated eyes, coughing or wheezing.</p>\r\n\r\n<p>Everyone should&nbsp;<strong>reduce</strong>&nbsp;prolonged or heavy physical activity.</p>\r\n\r\n<p>People over 65, children 14 years and younger, pregnant women and those with existing heart or lung conditions should&nbsp;<strong>avoid</strong>&nbsp;prolonged or heavy physical activity altogether.</p>\r\n\r\n<p>Anyone with a heart or lung condition should take their medication as prescribed by their doctor.</p>\r\n\r\n<p>People with asthma should follow their asthma management plan.</p>\r\n\r\n<p>Anyone with concerns about their health should seek medical advice or call NURSE-ON-CALL on&nbsp;<a href="tel:1300606024">1300 60 60 24</a>.</p>\r\n\r\n<p><strong>For further information, updates and advice relating to incidents affecting air quality in this area, please go to&nbsp;<a href="http://emergency.vic.gov.au/respond">http://emergency.vic.gov.au/respond</a></strong></p>',
        'background_colour': '#DD5900',
        'foreground_colour': '#FFFFFF'
    }, {
        'level': 5,
        'threshold_value': 177.99,
        'description': 'Very unhealthy all',
        'value_range': '107.0-177.9',
        'visibility': '1.5 - 2 km',
        'message': '<table border="0" cellpadding="0" cellspacing="0">\r\n\t<tbody>\r\n\t\t<tr>\r\n\t\t\t<td>\r\n\t\t\t<p>Excessive smoke levels can not only aggravate existing heart or lung conditions, but may also cause members of the community to experience irritated eyes, coughing or wheezing.</p>\r\n\r\n\t\t\t<p>Everyone should&nbsp;<strong>avoid</strong>&nbsp;prolonged or heavy physical activity.</p>\r\n\r\n\t\t\t<p>People over 65, children 14 years and younger, pregnant women and those with existing heart or lung conditions should&nbsp;<strong>avoid all</strong>&nbsp;physical activity outdoors.</p>\r\n\r\n\t\t\t<p>Anyone with a heart or lung condition should take their medication as prescribed by their doctor.</p>\r\n\r\n\t\t\t<p>People with asthma should follow their asthma management plan.</p>\r\n\r\n\t\t\t<p>Anyone with concerns about their health should seek medical advice or call NURSE-ON-CALL on&nbsp;<a href="tel:1300606024">1300 60 60 24</a>.</p>\r\n\r\n\t\t\t<p><strong>For further information, updates and advice relating to incidents affecting air quality in this area, please go to&nbsp;<a href="http://emergency.vic.gov.au/respond">http://emergency.vic.gov.au/respond</a></strong></p>\r\n\t\t\t</td>\r\n\t\t</tr>\r\n\t</tbody>\r\n</table>',
        'background_colour': '#D81E05',
        'foreground_colour': '#FFFFFF'
    }, {
        'level': 6,
        'threshold_value': 250.99,
        'description': 'Hazardous high',
        'value_range': 'Greater than 177',
        'visibility': '1 - 1.5 km',
        'message': '<p>Excessive smoke levels can not only aggravate existing heart or lung conditions, but may also cause members of the community to experience irritated eyes, coughing or wheezing.</p>\r\n\r\n<p>Everyone should&nbsp;<strong>avoid all</strong>&nbsp;outdoor physical activity.</p>\r\n\r\n<p>People over 65, children 14 years or younger, pregnant women and people with existing heart or lung conditions should remain indoors and keep physical activity levels as low as possible. These groups should also consider taking a break from the smoke by visiting a friend or relative.</p>\r\n\r\n<p>Anyone experiencing symptoms that may be due to smoke exposure should consider taking a break away from the smoky conditions.</p>\r\n\r\n<p>Anyone with a heart or lung condition should take their medication as prescribed by their doctor.</p>\r\n\r\n<p>People with asthma should follow their asthma management plan.</p>\r\n\r\n<p>Anyone with concerns about their health should seek medical advice or call NURSE-ON-CALL on&nbsp;<a href="tel:1300606024">1300 60 60 24</a>.</p>\r\n\r\n<p><strong>For further information, updates and advice relating to incidents affecting air quality in this area, please go to&nbsp;<a href="http://emergency.vic.gov.au/respond">http://emergency.vic.gov.au/respond</a></strong></p>',
        'background_colour': '#9B301C',
        'foreground_colour': '#FFFFFF'
    }, {
        'level': 2,
        'threshold_value': 25.99,
        'description': 'MODERATE',
        'value_range': '9.0-25.9',
        'visibility': '10 - 20 km',
        'message': '<p>Over the last 24 hours, the average level of PM2.5 particles in the air has met the &#39;moderate&#39; health category. This means that the level of PM2.5 particles in the air can be considered healthy for everyone.<br />\r\n<br />\r\nThis health category is based on the 24-hour rolling average only.<br />\r\n<br />\r\nThere is no cautionary advice for this health category.<br />\r\n<br />\r\n<strong>For information, updates and advice relating to incidents affecting air quality in this area please go to: <a href="http://emergency.vic.gov.au/respond/">http://emergency.vic.gov.au/respond/</a></strong></p>',
        'background_colour': '#3A75C4',
        'foreground_colour': '#FFFFFF'
    }, {
        'level': 7,
        'threshold_value': 99999999.99,
        'description': 'Hazardous extreme',
        'value_range': 'Greater than 250',
        'visibility': '0.5 - 1 km',
        'message': '<p>Excessive smoke levels can not only aggravate existing heart or lung conditions, but may also cause members of the community to experience irritated eyes, coughing or wheezing.</p>\r\n\r\n<p>Everyone should&nbsp;<strong>avoid all</strong>&nbsp;outdoor physical activity.</p>\r\n\r\n<p>People over 65, children 14 years or younger, pregnant women and people with heart or lung conditions should remain indoors and keep physical activity levels as low as possible. These groups should also consider taking a break away from the smoke by visiting a friend or relative.</p>\r\n\r\n<p>Anyone experiencing symptoms that may be due to smoke exposure should consider taking a break away from the smoky conditions.</p>\r\n\r\n<p>Anyone with a heart or lung condition should take their medication as prescribed by their doctor.</p>\r\n\r\n<p>People with asthma should follow their asthma management plan.</p>\r\n\r\n<p>Anyone with concerns about their health should seek medical advice or call NURSE-ON-CALL on&nbsp;<a href="tel:1300606024">1300 60 60 24</a>.</p>\r\n\r\n<p><strong>For further information, updates and advice relating to incidents affecting air quality in this area, please go to&nbsp;<a href="http://emergency.vic.gov.au/respond">http://emergency.vic.gov.au/respond</a></strong></p>',
        'background_colour': '#6B3021',
        'foreground_colour': '#FFFFFF'
    }
]

def insert_aqi_categories(apps, schema_editor):
    AQICategoryThreshold = apps.get_model(
        'au_epa_data', 'AQICategoryThreshold')
    for aqi in AQI_CATEGORY_THRESHOLDS:
        AQICategoryThreshold.objects.get_or_create(**aqi)


def insert_health_categories(apps, schema_editor):
    HealthCategoryThreshold = apps.get_model(
        'au_epa_data', 'HealthCategoryThreshold')
    for he in HEALTH_CATEGORY_THRESHOLD:
        HealthCategoryThreshold.objects.get_or_create(**he)


def revert_aqi_categories(apps, schema_editor):
    AQICategoryThreshold = apps.get_model(
        'au_epa_data', 'AQICategoryThreshold')
    AQICategoryThreshold.objects.all().delete()

    HealthCategoryThreshold = apps.get_model(
        'au_epa_data', 'HealthCategoryThreshold')
    HealthCategoryThreshold.objects.all().delete()


def revert_health_categories(apps, schema_editor):
    AQICategoryThreshold = apps.get_model(
        'au_epa_data', 'AQICategoryThreshold')
    AQICategoryThreshold.objects.all().delete()

    HealthCategoryThreshold = apps.get_model(
        'au_epa_data', 'HealthCategoryThreshold')
    HealthCategoryThreshold.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('au_epa_data', '0007_monitor_slug'),
    ]

    operations = [
        migrations.RunPython(insert_aqi_categories, revert_aqi_categories),
        migrations.RunPython(insert_health_categories, revert_health_categories),
    ]
