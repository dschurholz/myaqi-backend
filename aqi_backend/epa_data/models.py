from django.utils.translation import ugettext_lazy as _
from django.db import models


class AbstractHourlyMeasure(models.Model):
    state_code = models.CharField(
        _("State code"), max_length=3, blank=True, null=True)
    county_code = models.CharField(
        _("County code"), max_length=3, blank=True, null=True)
    site_num = models.CharField(
        _("Site number"), max_length=4, blank=True, null=True)
    parameter_code = models.CharField(
        _("Parameter code"), max_length=5, blank=True, null=True)
    poc = models.SmallIntegerField(
        _("POC"), blank=True, null=True)
    latitude = models.FloatField(
        _("Latitude"), blank=True, null=True)
    longitude = models.FloatField(
        _("Longitude"), blank=True, null=True)
    datum = models.CharField(
        _("Datum"), max_length=8, blank=True, null=True)
    parameter_name = models.CharField(
        _("Parameter Name"), max_length=32, blank=True, null=True)
    date_local = models.DateField(_("Local date"), blank=True, null=True)
    time_local = models.TimeField(_("Local time"), blank=True, null=True)
    date_gmt = models.DateField(_("GMT date"), blank=True, null=True)
    time_gmt = models.TimeField(_("GMT time"), blank=True, null=True)
    sample_measurement = models.FloatField(
        _("Sample measurement"), blank=True, null=True)
    units_of_measure = models.CharField(
        _("Units of measurement"), max_length=64, blank=True, null=True)
    mdl = models.FloatField(
        _("MDL"), blank=True, null=True)
    unceirtanty = models.CharField(
        _("Unceirtanty"), max_length=32, blank=True, null=True)
    qualifier = models.CharField(
        _("Qualifier"), max_length=32, blank=True, null=True)
    method_type = models.CharField(
        _("Method type"), max_length=32, blank=True, null=True)
    method_code = models.CharField(
        _("Method code"), max_length=32, blank=True, null=True)
    method_name = models.CharField(
        _("Method name"), max_length=128, blank=True, null=True)
    state_name = models.CharField(
        _("State name"), max_length=64, blank=True, null=True)
    county_name = models.CharField(
        _("County name"), max_length=64, blank=True, null=True)
    date_of_last_change = models.DateField(
        _("Date of last change"), blank=True, null=True)

    @property
    def min_format(self):
        return (self.parameter_name, self.sample_measurement,
                self.units_of_measure)

    class Meta:
        abstract = True


class Pm10Hourly(AbstractHourlyMeasure):

    class Meta:
        db_table = 'pm10_hourly'
        verbose_name = _('PM 10 Hourly Measurement')
        verbose_name_plural = _('PM 10 Hourly Measurements')


class Pm25Hourly(AbstractHourlyMeasure):

    class Meta:
        db_table = 'pm25_hourly'
        verbose_name = _('PM 2.5 Hourly Measurement')
        verbose_name_plural = _('PM 2.5 Hourly Measurements')


class COHourly(AbstractHourlyMeasure):

    class Meta:
        db_table = 'co2_hourly'
        verbose_name = _('CO Hourly Measurement')
        verbose_name_plural = _('CO Hourly Measurements')


class NO2Hourly(AbstractHourlyMeasure):

    class Meta:
        db_table = 'no2_hourly'
        verbose_name = _('NO2 Hourly Measurement')
        verbose_name_plural = _('NO2 Hourly Measurements')


class SO2Hourly(AbstractHourlyMeasure):

    class Meta:
        db_table = 'so2_hourly'
        verbose_name = _('SO2 Hourly Measurement')
        verbose_name_plural = _('SO2 Hourly Measurements')


class O3Hourly(AbstractHourlyMeasure):

    class Meta:
        db_table = 'o3_hourly'
        verbose_name = _('O3 Hourly Measurement')
        verbose_name_plural = _('O3 Hourly Measurements')


class TemparatureHourly(AbstractHourlyMeasure):

    class Meta:
        db_table = 'temperature_hourly'
        verbose_name = _('Temperature Hourly Measurement')
        verbose_name_plural = _('Temperature Hourly Measurements')


class HumidityHourly(AbstractHourlyMeasure):

    class Meta:
        db_table = 'humidity_hourly'
        verbose_name = _('Humidity Hourly Measurement')
        verbose_name_plural = _('Humidity Hourly Measurements')


class WindHourly(AbstractHourlyMeasure):

    class Meta:
        db_table = 'wind_hourly'
        verbose_name = _('Wind Hourly Measurement')
        verbose_name_plural = _('Wind Hourly Measurements')


class AtmosphericPressureHourly(AbstractHourlyMeasure):

    class Meta:
        db_table = 'atm_perssure_hourly'
        verbose_name = _('Atmospheric Pressure Hourly Measurement')
        verbose_name_plural = _('Atmospheric Pressure Hourly Measurements')
