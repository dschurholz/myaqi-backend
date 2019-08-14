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

To install the historical traffic information for 2017 and 2018 for 6 traffic measuring stations in Melbourne, execute the following commands:

    $ ./manage.py shell

in the python console run:

    >>> from geo_data import load_traffic_flows
    >>> load_traffic_flows.run()

## Historical Fire Incidents Data

To install the historical fire incidents information for 2017 and 2018 all over the Victoria region, execute the following commands:

    $ ./manage.py shell

in the python console run:

    >>> from geo_data import load_fires
    >>> load_fires.run()    
