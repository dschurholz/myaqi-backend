# AU EPA Data

This module contains all the necessary logic to manage the data for the Victorian EPA air quality data. For more information see [EPAAQAPIWebServicesSpecification.pdf](https://github.com/dschurholz/myaqi-backend/tree/master/docs/external/EPAAQAPIWebServicesSpecification.pdf).

### Importing AQ data

Run the following commands (with the virtualenv activate and on aqi_backend/ directory) to import the data to populate this module's models. Please follow the order for foreign keys to work properly.

Importing Sites:

    $ ./manage.py au_epa_update --type site

Importing Monitors (Pollutants and Meteorological Variables):

    $ ./manage.py au_epa_update --type monitor

Importing Time Basis (Time periods of monitor measurements):

    $ ./manage.py au_epa_update --type time_basis

Importing Measurements (be careful with the date ranges as the database can end up filling the computer storage):

    $ ./manage.py au_epa_update --type measurement --url_args '{"siteId":10001,"monitorId":"sp_AQI","timebasisid":"1HR_AV","fromDate":"31031800","toDate":"01041800"}'

*Note: the values of the url_args are as follows:*
    
- siteId: integer id for the monitoring staions
- monitorId: string id for the pollutant
- timebasisid: 1HR_AV, 8HR_RAV or 24HR_RAV
- fromDate: start date for retrieving measurements; format: DDMMYYHH
- toDate: end date for retrieving measurements; format: DDMMYYHH