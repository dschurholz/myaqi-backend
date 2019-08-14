# MyAQI Backend & API

This repository contains a Django backend project for the MyAQI tool:

 - Users can request live information for Melbourne's Air Quality information.
 - Users can set their profile preferences for customised views and colours.
 - Users can see forecasts for Air Pollutant levels in their area.
 - Users can watch the possible sources of pollution in the Melbourne Urban area like fire incidents and traffic congestion.
 - This tool also provides statistical analysis of the prediction methods used, as a console service.

### Used technologies and python dependencies

*Backend:*

 - Python 3.6
 - Postgresql 10.10 + PostGIS 2.4
 - [Django](https://github.com/django/django)
 - [Psycopg2](https://github.com/psycopg/psycopg2)
 - [Django Suit](https://github.com/darklow/django-suit)
 - [Django Channels](https://github.com/django/channels)
 - [Django Rest Framework](https://www.django-rest-framework.org/)
 - [Django](https://www.djangoproject.com/)
 - [Keras](https://keras.io/)
 - [Matplot Lib](https://matplotlib.org/)
 - [Pandas](https://pandas.pydata.org/)
 - [PostGIS](https://postgis.net/)
 - [PostgreSQL](https://www.postgresql.org/)
 - [Sklearn](https://scikit-learn.org/stable/)
 - [Tensor Flow](https://www.tensorflow.org/)

*Data sources:*

 - [Bing Maps API](http://dev.virtualearth.net/REST/v1/Traffic/Incidents/)
 - [Google Maps JavaScript API](https://developers.google.com/maps/documentation/javascript/tutorial)
 - [Victoria Emergency API](http://emergency.vic.gov.au/public/osom-geojson.json)
 - [Victoria EPA AirWatch API](http://sciwebsvc.epa.vic.gov.au/aqapi/)
 - [Victoria Roads API](https://traffic.vicroads.vic.gov.au/maps.js)
 - [Weather Bit API](https://api.weatherbit.io/v2.0/forecast/airquality)

*Frontend:*
[MyAQI Frontend Repository](https://www.github.com/dschurholz/myaqi-frontend.git)

 - [ReactJS](https://reactjs.org/)
 - [Core-UI](https://coreui.io/)

For the exact versions check the project's `requirements.txt` file.

## Installing MyAQI

Some requirements before installing myaqi-backend:

Install Python 3 if not already installed in your OS. I recommend using [PyEnv](https://github.com/pyenv/pyenv) on Linux to manage your favourite python versions.

Install Postgresql and create the following databases `epa_aqi`, `au_epa_aqi` and `geo_data`, with the postgresql role `epa_master` and a desired password. You can choose your own names, but remember to reset it on the `settings_local.py` file. Then install PostGIS ([linux](https://www.mananpatel.in/postgis-installation-in-ubuntu-18-04-lts-bionic-beaver/)) and add the extension to the `geo_data` database:

    geo_data=# CREATE EXTENSION postgis;

To Install myaqi-backend you need to create a virtualenv:

if you have not installed virtualenv:

    $ sudo apt-get install python-virtualenv
or
    $ pip3 install virtualenv

then you need to run (always check that you are using python 3):

    $ virtualenv myaqi-backend -p /usr/bin/python3
    $ cd myaqi-backend

and you are ready to clone the repo:

    $ git clone https://github.com/dschurholz/myaqi-backend.git
    $ cd myaqi-backend

Once on myaqi-backend directory, you need to run

    $ source ../bin/activate

to activate the virtual-environment. Be sure that your command line looks similar to this (notice the activated virtual-environment at the start):

    (myaqi-backend) <user>@<computer-name>:/current/location$ ...

Then install all the project's dependencies with:

    $ pip install -r requirements.txt

Then you need to install the GDAL libraries for geodjango to work. On linux do the following (taken from [GeoDjango](https://docs.djangoproject.com/en/2.2/ref/contrib/gis/install/geolibs/):

    $ sudo apt-get install binutils libproj-dev gdal-bin

Before starting to run the project, you need to set up the settings, execute:

    $ cd myaqi-backend/myaqi
    $ cp settings_local.py.example settings_local.py

and change database default settings to your settings in the settings_local.py file.

Then you are ready to populate the databases with:

    $ ./manage.py migrate
    $ ./manage.py migrate au_epa_data --database au_epa_aqi
    $ ./manage.py migrate geo_data --database geo_data

Finally, try the test server to prove everything is well configured:

    $ ./manage.py runserver

to test you can got to [http://localhost:8000/admin](http://localhost:8000/admin)

Create a superuser for the admin interface by running:

    $ ./manage.py createsuperuser

and follow the prompt.

### Data sets and Populating Databases

The MyAQI tool requires many different datasets to work properly. To try the PostGIS installation you can install the World Borders dataset, it could also be handy for further expansions of the tool. Follow the steps in [Geo Data Readme](https://github.com/dschurholz/myaqi-backend/tree/master/aqi_backend/geo_data).