# Geo Data

## World Data

Follow the next steps to import the World Data dataset:

    $ cd geo_data/
    $ mkdir -p data/world/
    $ cd data/world
    $ wget https://thematicmapping.org/downloads/TM_WORLD_BORDERS-0.3.zip
    $ unzip TM_WORLD_BORDERS-0.3.zip
    $ cd ../.. 
    $ ./manage.py shell

in the python console run:

    >>> from geo_data import load_world_borders
    >>> load_world_borders.run()

Check the GeoDjango installation by opening the following link [http://localhost:8000/admin/geo_data/worldborder/](http://localhost:8000/admin/geo_data/worldborder/) and checking that the map is shown when clicking on any country.

## Historical Traffic Data

First download the `traffic.zip` file from [here](https://drive.google.com/open?id=1ObIRuFzK-nJj5WIq0zdXKt7kJ7c0hQ6c).
To install the historical traffic information for 2017 and 2018 for 6 traffic measuring stations in Melbourne, execute the following commands:

    $ cd geo_data/
    $ mkdir -p data/traffic/
    $ cd data/traffic
    $ mv path/to/traffic.zip .
    $ unzip traffic.zip
    $ unzip 2017.zip && unzip 2018.zip
    $ cd ../../..
    $ ./manage.py shell

in the python console run:

    >>> from geo_data import load_traffic_flows
    >>> load_traffic_flows.run()

## Historical Fire Incidents Data

First download the `fire.zip` file from [here](https://drive.google.com/open?id=1EMk5UfIWfPZbyEy0lwG7tyoX9oRjcQcn).
To install the historical fire incidents information for 2017 and 2018 all over the Victoria region, execute the following commands:

    $ cd geo_data/
    $ mkdir data/
    $ cd data/
    $ mv path/to/fire.zip .
    $ unzip fire.zip
    $ cd ..
    $ ./manage.py shell

in the python console run:

    >>> from geo_data import load_fires
    >>> load_fires.run()    
