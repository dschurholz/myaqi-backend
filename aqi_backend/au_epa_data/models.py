import logging
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db import IntegrityError
from django.utils.text import slugify
from ckeditor.fields import RichTextField

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

    def __str__(self):
        return "{0}-{1}".format(self.site_id, self.name)

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


class HealthCategoryThreshold(models.Model):
    level = models.PositiveSmallIntegerField(_("Level"), primary_key=True)
    threshold_value = models.FloatField(
        _("Threshold Value"), blank=True, null=True)
    description = models.CharField(
        _("Description"), max_length=63, blank=True, null=True)
    value_range = models.CharField(
        _("Value Range"), max_length=63, blank=True, null=True)
    visibility = models.CharField(
        _("Visibility"), max_length=63, blank=True, null=True)
    message = RichTextField(_("Message"), blank=True, null=True)
    background_colour = models.CharField(
        _("Background Colour"), max_length=7, blank=True, null=True)
    foreground_colour = models.CharField(
        _("Foreground Colour"), max_length=7, blank=True, null=True)

    def __str__(self):
        return "{0}-{1}".format(self.level, self.description)

    class Meta:
        db_table = 'health_category_threshold'
        verbose_name = _('Health Category Threshold')
        verbose_name_plural = _('Health Category Thresholds')


class AQICategoryThreshold(models.Model):
    abbreviation = models.CharField(
        _("Abbrevation"), primary_key=True, max_length=2)
    lower_threshold_value = models.FloatField(
        _("Lower Threshold Value"), blank=True, null=True)
    upper_threshold_value = models.FloatField(
        _("Upper Threshold Value"), blank=True, null=True)
    description = models.CharField(
        _("Description"), max_length=63, blank=True, null=True)
    background_colour = models.CharField(
        _("Background Colour"), max_length=7, blank=True, null=True)
    foreground_colour = models.CharField(
        _("Foreground Colour"), max_length=7, blank=True, null=True)

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'aqi_category_threshold'
        verbose_name = _('AQI Category Threshold')
        verbose_name_plural = _('AQI Category Thresholds')


class Measurement(UpdateM2MModel):
    date_time_start = models.DateTimeField(_("Date Time Start"))
    date_time_recorded = models.DateTimeField(_("Date Time Recorded"))
    value = models.CharField(
        _("Value"), max_length=31, blank=True, null=True)
    quality_status = models.PositiveSmallIntegerField(
        _("Quality Status"), default=9)
    aqi_index = models.PositiveSmallIntegerField(
        _("AQI Index"), default=0)
    aqi_category_threshold = models.ForeignKey(
        AQICategoryThreshold, verbose_name=_("AQI Category"), blank=True,
        null=True, on_delete=models.DO_NOTHING)
    health_category_threshold = models.ForeignKey(
        HealthCategoryThreshold, verbose_name=_("Health Category"), blank=True,
        null=True, on_delete=models.DO_NOTHING)
    site = models.ForeignKey(
        Site, verbose_name=_("Site"), blank=True, null=True,
        on_delete=models.DO_NOTHING)
    time_basis = models.ForeignKey(
        TimeBasis, verbose_name=_("Time Basis"), blank=True, null=True,
        on_delete=models.DO_NOTHING)
    monitor = models.ForeignKey(
        Monitor, verbose_name=_("Monitor"), blank=True, null=True,
        on_delete=models.DO_NOTHING)
    monitor_time_basis = models.ForeignKey(
        MonitorTimeBasis, verbose_name=_("Monitor Time Basis"), blank=True,
        null=True, on_delete=models.DO_NOTHING)
    equipment_type = models.ForeignKey(
        EquipmentType, verbose_name=_("Equipment Type"), blank=True, null=True,
        on_delete=models.DO_NOTHING)

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

    class Meta:
        db_table = 'measurement'
        verbose_name = _('Measurement')
        verbose_name_plural = _('Measurements')
        unique_together = (
            ('date_time_start', 'site', 'monitor', 'time_basis'), )
