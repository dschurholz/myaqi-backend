import logging
import copy
from django.utils.translation import ugettext_lazy as _
from django.db import models, IntegrityError, connections
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Avg
from django.db.models.functions import Cast
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import GEOSGeometry

from geo_data.utils import with_metric_buffer
from forecasting.constants import (
    FIRE_SITUATIONS_RADIUS, FIRE_SITUATION_STATION_RADIUS)

logger = logging.getLogger('myaqi')


class UpdateM2MModel(models.Model):
    def update_m2m_field(self, m2m_field, entries):
        raise NotImplementedError(
            "Child classes of the UpdateM2MModel must implement the "
            "update_m2m_field method.")

    class Meta:
        abstract = True


class SiteList(models.Model):
    name = models.CharField(_("Name"), max_length=63, primary_key=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'site_list'
        verbose_name = _('Site List')
        verbose_name_plural = _('Site Lists')


class Site(UpdateM2MModel):
    site_id = models.IntegerField(_("Site ID"), primary_key=True)
    name = models.CharField(_("Name"), max_length=63, blank=True, null=True)
    latitude = models.DecimalField(
        _("Latitude"), max_digits=16, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(
        _("Longitude"), max_digits=16, decimal_places=6, blank=True, null=True)
    fire_hazard_category = models.PositiveSmallIntegerField(
        _("Fire Hazard Category"), blank=True, null=True)
    is_station_offline = models.BooleanField(
        _("Is Station Offline"), default=False)
    has_incident = models.BooleanField(_("Has Incident"), default=False)
    incident_type = models.CharField(
        _("Incident Type"), max_length=31, blank=True, null=True)
    site_list = models.ManyToManyField(
        SiteList, verbose_name=_("Site List"), blank=True)
    _fire_area_radius = 50 * 1000  # in meters

    def __str__(self):
        return "{0}-{1}".format(self.site_id, self.name)

    @property
    def location_point(self):
        return Point(float(self.longitude), float(self.latitude))

    @property
    def fire_area(self):
        # return with_metric_buffer(self.location_point, self._fire_area_radius)
        raw_query = (
            "SELECT ST_Buffer(ST_GeomFromText('{location_point}', 4326)"
            "::geography, {radius})".format(
                location_point=self.location_point,
                radius=self._fire_area_radius
            )
        )
        fire_area = None
        with connections['geo_data'].cursor() as cursor:
            cursor.execute(raw_query)
            fire_area = GEOSGeometry(cursor.fetchone()[0])

        return fire_area

    @property
    def fire_areas(self):
        return self.get_fire_situations_areas()

    def set_fire_area_radius(self, fire_area_radius=None):
        if fire_area_radius is not None:
            site_radius = fire_area_radius
        else:
            site_radius = FIRE_SITUATION_STATION_RADIUS[str(self.site_id)]

        self._fire_area_radius = site_radius
        return self._fire_area_radius

    def get_fire_situations_areas(self, furthest_fire_area_radius=None):
        areas = []
        if furthest_fire_area_radius is not None:
            furthest_radius = furthest_fire_area_radius
        else:
            furthest_radius = FIRE_SITUATION_STATION_RADIUS[str(self.site_id)]

        for situation, radius_prop in FIRE_SITUATIONS_RADIUS.items():
            self.set_fire_area_radius(furthest_radius * radius_prop)
            areas.append(self.fire_area)

        return areas

    def update_m2m_field(self, m2m_field, entries):
        from .constants import SITE_LIST

        if m2m_field == SITE_LIST:
            self.site_list.add(*entries)
            return True
        return False

    class Meta:
        db_table = 'site'
        verbose_name = _('Site')
        verbose_name_plural = _('Sites')


class IncidentSite(models.Model):
    emv_url = models.URLField(_("EMV Url"), blank=True, null=True)
    incident_icon = models.URLField(
        _("Incident Icon URL"), blank=True, null=True)
    site = models.ForeignKey(
        Site, verbose_name=_("Site"), on_delete=models.CASCADE,
        related_name="incidents", blank=True, null=True)

    def __str__(self):
        return str(self.site)

    class Meta:
        db_table = 'incident_site'
        verbose_name = _('Incident Site')
        verbose_name_plural = _('Incident Sites')


class EquipmentType(models.Model):
    id_number = models.IntegerField(_("Id Number"), blank=True, null=True)
    code = models.CharField(
        _("Code"), max_length=31, blank=True, null=True)
    description = models.CharField(
        _("Description"), max_length=63, blank=True, null=True)

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'equipment_type'
        verbose_name = _('Equipment Type')
        verbose_name_plural = _('Equipment Types')


class Monitor(UpdateM2MModel):
    monitor_id = models.CharField(
        _("Monitor ID"), max_length=15, primary_key=True)
    slug = models.SlugField(
        max_length=15, db_index=True, blank=True, null=True)
    short_name = models.CharField(
        _("Short Name"), max_length=31, blank=True, null=True)
    common_name = models.CharField(
        _("Common Name"), max_length=31, blank=True, null=True)
    epa_description_url = models.URLField(
        _("EPA Description URL"), blank=True, null=True)
    unit_of_measure = models.CharField(
        _("Unit Of Measure"), max_length=15, blank=True, null=True)
    presentation_precision = models.PositiveSmallIntegerField(
        _("Presentation Precision"), default=0)
    equipment_type = models.ForeignKey(
        EquipmentType, verbose_name=_("Equipment Type"), blank=True, null=True,
        on_delete=models.DO_NOTHING)
    sites = models.ManyToManyField(
        Site, verbose_name=_("Sites"), related_name="monitors")

    def __str__(self):
        return self.monitor_id

    def update_m2m_field(self, m2m_field, entries):
        from .constants import SITES

        if m2m_field == SITES:
            try:
                self.sites.add(*entries)
            except IntegrityError as e:
                logger.error(e)
                return False
            return True
        return False

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.monitor_id)

        super(Monitor, self).save(*args, **kwargs)

    class Meta:
        db_table = 'monitor'
        verbose_name = _('Monitor')
        verbose_name_plural = _('Monitors')


class TimeBasis(UpdateM2MModel):
    time_base_id = models.CharField(
        _("Time Base Id"), max_length=15, primary_key=True)
    description = models.CharField(
        _("Description"), max_length=63, blank=True, null=True)
    is_rolling_average = models.PositiveSmallIntegerField(
        _("Is Rolling Average"), default=0)
    rolling_average_period = models.PositiveSmallIntegerField(
        _("Rolling Average Period"), blank=True, null=True)
    min_data_percent = models.PositiveSmallIntegerField(
        _("Min Data Percent"), default=0)
    time_basis_desc_url = models.URLField(
        _("Time Basis Desc URL"), blank=True, null=True)
    sites = models.ManyToManyField(
        Site, verbose_name=_("Sites"), related_name="time_basis")

    def __str__(self):
        return self.time_base_id

    def update_m2m_field(self, m2m_field, entries):
        from .constants import SITES

        if m2m_field == SITES:
            try:
                self.sites.add(*entries)
            except IntegrityError as e:
                logger.error(e)
                return False
            return True
        return False

    class Meta:
        db_table = 'time_basis'
        verbose_name = _('Time Basis')
        verbose_name_plural = _('Time Basis')


class MonitorTimeBasis(models.Model):
    time_basis = models.ForeignKey(
        TimeBasis, verbose_name=_("Time Basis Id"),
        related_name="monitor_time_basis", on_delete=models.DO_NOTHING)
    monitor = models.ForeignKey(
        Monitor, verbose_name=_("Monitor Id"),
        related_name="monitor_time_basis", on_delete=models.DO_NOTHING)
    aqi_pollutant_standard = models.FloatField(
        _("AQI Pollutant Standard"), blank=True, null=True)
    incident_type = models.CharField(
        _("Incident Type"), max_length=31, blank=True, null=True)
    presentation_order = models.PositiveSmallIntegerField(
        _("Presentation Order"), blank=True, null=True)
    calc_aqi = models.BooleanField(_("Calc AQI"), default=False)
    calc_health_category = models.BooleanField(
        _("Calc Health Category"), default=False)

    def __str__(self):
        return "{0}-{1}".format(self.monitor_id, self.time_basis_id)

    class Meta:
        db_table = 'monitor_time_basis'
        verbose_name = _('Monitor Has Time Basis')
        verbose_name_plural = _('Monitor Has Time Basis')


class Measurement(UpdateM2MModel):
    date_time_start = models.DateTimeField(_("Date Time Start"))
    date_time_recorded = models.DateTimeField(_("Date Time Recorded"))
    value = models.CharField(
        _("Value"), max_length=31, blank=True, null=True)
    quality_status = models.PositiveSmallIntegerField(
        _("Quality Status"), default=9)
    aqi_index = models.PositiveSmallIntegerField(
        _("AQI Index"), default=0)
    aqi_category_threshold = models.PositiveSmallIntegerField(
        _("AQI Category"), blank=True, null=True)
    health_category_threshold = models.PositiveSmallIntegerField(
        _("Health Category"), blank=True, null=True)
    site = models.ForeignKey(
        Site, verbose_name=_("Site"), blank=True, null=True,
        on_delete=models.DO_NOTHING, related_name='measurements')
    time_basis = models.ForeignKey(
        TimeBasis, verbose_name=_("Time Basis"), blank=True, null=True,
        on_delete=models.DO_NOTHING, related_name='measurements')
    monitor = models.ForeignKey(
        Monitor, verbose_name=_("Monitor"), blank=True, null=True,
        on_delete=models.DO_NOTHING, related_name='measurements')
    monitor_time_basis = models.ForeignKey(
        MonitorTimeBasis, verbose_name=_("Monitor Time Basis"), blank=True,
        null=True, on_delete=models.DO_NOTHING, related_name='measurements')
    equipment_type = models.ForeignKey(
        EquipmentType, verbose_name=_("Equipment Type"), blank=True, null=True,
        on_delete=models.DO_NOTHING, related_name='measurements')

    def __str__(self):
        return self.monitor_id

    def update_m2m_field(self, m2m_field, entries):
        from .constants import SITES

        if m2m_field == SITES:
            try:
                self.sites.add(*entries)
            except IntegrityError as e:
                logger.error(e)
                return False
            return True
        return False

    @classmethod
    def measurements_for_forecast(
            cls, measurements, aq_attributes, start_date, end_date):

        from .constants import DATETIME_FORMAT, POLLUTANT_TO_MONITOR
        from forecasting.utils import get_datetime_span_dict

        print(start_date, end_date)
        dates = get_datetime_span_dict(start_date, end_date)
        data = {
            'date': []
        }
        averages = {}
        measurements = measurements.filter(
            date_time_start__gte=start_date,
            date_time_start__lte=end_date)

        # Get the average for each aq_attr to mend missing pieces
        # and create the data columns
        for attr in aq_attributes:
            avg = measurements.filter(monitor_id=attr).annotate(
                value_float=Cast('value', models.FloatField())).aggregate(
                    Avg('value_float'))
            averages[attr] = round(avg['value_float__avg'], 2)
            data[POLLUTANT_TO_MONITOR[attr]] = []

        for m in measurements:
            date_str = timezone.localtime(
                m.date_time_start).strftime(DATETIME_FORMAT)
            # print(date_str, m.monitor, m.value)
            # if date_str not in dates.keys():
            #     dates[date_str] = []
            # print (date_str)
            dates[date_str].append((
                m.monitor.monitor_id, m.value
            ))
        for date, monitors in dates.items():
            # print(date, len(monitors))
            data['date'].append(date)
            aq_attr_checklist = copy.copy(aq_attributes)
            for monitor in monitors:
                aq_attr_checklist.remove(monitor[0])
                moni = POLLUTANT_TO_MONITOR[monitor[0]]
                data[moni].append(monitor[1])
            for attr in aq_attr_checklist:
                moni = POLLUTANT_TO_MONITOR[attr]
                data[moni].append(averages[attr])

        print(averages)
        return data

    class Meta:
        db_table = 'measurement'
        verbose_name = _('Measurement')
        verbose_name_plural = _('Measurements')
        unique_together = (
            ('date_time_start', 'site', 'monitor', 'time_basis'), )
