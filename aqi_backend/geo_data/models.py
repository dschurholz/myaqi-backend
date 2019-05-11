import copy
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models
from django.utils import timezone
from django.db.models import Avg

from forecasting.utils import get_datetime_span_dict
from forecasting.constants import TRAFFIC_FLOW_TITLE_PREFIX
from au_epa_data.constants import DATETIME_FORMAT


class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField(_('Population 2005'))
    fips = models.CharField(_('FIPS Code'), max_length=2)
    iso2 = models.CharField(_('2 Digit ISO'), max_length=2)
    iso3 = models.CharField(_('3 Digit ISO'), max_length=3)
    un = models.IntegerField(_('United Nations Code'))
    region = models.IntegerField(_('Region Code'))
    subregion = models.IntegerField(_('Sub-Region Code'))
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField)
    mpoly = models.MultiPolygonField()

    # Returns the string representation of the model.
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'world_border'
        verbose_name = _('World Border')
        verbose_name_plural = _('World Borders')
        ordering = ('name', )


class Fire(models.Model):
    firetype = models.CharField(_('Fire Type'), max_length=8)
    season = models.IntegerField(_('Season'))
    fire_no = models.CharField(_('Fire Number'), max_length=25)
    name = models.CharField(_('Name'), max_length=254)
    start_date = models.DateField(_('Start Date'), null=True, blank=True)
    strtdatit = models.BigIntegerField(_('Start Date (Int)'))
    treat_type = models.CharField(_('Treatment Type'), max_length=50)
    fire_svrty = models.CharField(_('Fire Severity'), max_length=25)
    fire_cover = models.CharField(_('Fire Cover'), max_length=50)
    firekey = models.CharField(_('Fire Key'), max_length=50)
    cr_date = models.DateField(_('Creation Date'), null=True, blank=True)
    updatedate = models.DateField(_('Update Date'), null=True, blank=True)
    area_ha = models.FloatField(_('Area (Hectares)'))
    method = models.CharField(_('Method'), max_length=50)
    methd_cmnt = models.CharField(_('Method Comment'), max_length=254)
    accuracy = models.CharField(_('Accuracy'), max_length=50)
    dse_id = models.BigIntegerField(_('DSE Id'))
    cfa_id = models.BigIntegerField(_('CFA Id'))
    districtid = models.CharField(_('District Id'), max_length=2)
    geom = models.MultiPolygonField(_('Geometry'), srid=4326)

    @classmethod
    def fires_for_forecast(cls):
        return []

    @classmethod
    def get_fire_contains_situation(cls, location, seasons=[]):
        fires = cls.objects.all()
        if len(seasons) > 0:
            fires = fires.filter(season__in=seasons)
        fires = fires.filter(geom__contains=location)
        return fires

    @classmethod
    def get_fire_intersects_situation(cls, area, seasons=[]):
        fires = cls.objects.all()
        if len(seasons) > 0:
            fires = fires.filter(season__in=seasons)
        fires = fires.filter(geom__intersects=area)
        return fires

    class Meta:
        db_table = 'fire'
        verbose_name = _('Fire')
        verbose_name_plural = _('Fires')
        ordering = ('-season', '-start_date', 'name', )


class TrafficFlow(models.Model):
    nb_scats_site = models.PositiveIntegerField(_('NB Scats Site'))
    qt_interval_count = models.DateTimeField(_('QT Interval Count'))
    region_name = models.CharField(_('Region Name'), max_length=3)
    records_count = models.PositiveIntegerField(_('Records Count'))
    traffic_volume = models.PositiveIntegerField(_('Traffic Volume'))

    @classmethod
    def traffic_flows_for_forecast(
            cls, traffic_flow_ids, start_date, end_date):

        traffic_flows = cls.objects.filter(
            nb_scats_site__in=traffic_flow_ids,
            qt_interval_count__gte=start_date,
            qt_interval_count__lte=end_date).order_by('qt_interval_count')
        dates = get_datetime_span_dict(start_date, end_date)
        data = {
            'date': []
        }

        def get_traffic_label(s):
            return '{}_{}'.format(TRAFFIC_FLOW_TITLE_PREFIX, s)
        # Get the average for each station to mend missing pieces
        # and create the data columns
        averages = {}
        for avg in traffic_flows.values('nb_scats_site').annotate(
                Avg('traffic_volume')).order_by('traffic_volume__avg'):
            averages[str(avg['nb_scats_site'])] = round(
                avg['traffic_volume__avg'])
            data[get_traffic_label(avg['nb_scats_site'])] = []

        for tf in traffic_flows:
            date_str = timezone.localtime(tf.qt_interval_count).strftime(
                DATETIME_FORMAT)
            dates[date_str].append((
                tf.nb_scats_site, tf.traffic_volume
            ))

        for date, site_flows in dates.items():
            # if len(site_flows) != 4:
            #     print(date, site_flows, len(site_flows))
            data['date'].append(date)
            sites_ids_checklist = copy.copy(traffic_flow_ids)
            for site_flow in site_flows:
                # if len(site_flows) != 4:
                #     print(site_flow, sites_ids_checklist)
                try:
                    sites_ids_checklist.remove(str(site_flow[0]))
                except ValueError:
                    continue
                else:
                    data[get_traffic_label(site_flow[0])].append(site_flow[1])
            for site in sites_ids_checklist:
                data[get_traffic_label(site)].append(averages[site])

        print(averages)

        return data

    class Meta:
        db_table = 'traffic_flow'
        verbose_name = _('Traffic Flow')
        verbose_name_plural = _('Traffic Flows')
        ordering = ('-qt_interval_count', 'region_name', )