from django.utils.translation import ugettext_lazy as _
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.safestring import mark_safe


class AQIOrganization(models.Model):
    abbreviation = models.CharField(
        _("Abbrevation"), primary_key=True, max_length=5)
    name = models.CharField(
        _("Name"), max_length=127, blank=True, null=True)
    description = RichTextField(_("Description"), blank=True, null=True)
    logo = models.URLField(_("Logo"), blank=True, null=True)

    def logo_tag(self):
        return mark_safe(u'<img height="50px" src="{0}" />'.format(self.logo))
    logo_tag.short_description = 'Logo'

    def __str__(self):
        return self.abbreviation

    class Meta:
        db_table = 'aqi_organization'
        verbose_name = _('AQI Organization')
        verbose_name_plural = _('AQI Organizations')


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
    aqi_organization = models.ForeignKey(
        AQIOrganization, verbose_name=_("AQI Organization"),
        related_name=_("health_category_thresholds"),
        on_delete=models.DO_NOTHING, null=True, blank=True)
    pollutant = models.CharField(
        _("Pollutant"), max_length=15, default="sp_AQI")

    def __str__(self):
        return "{0}-{1}".format(self.level, self.description)

    class Meta:
        db_table = 'health_category_threshold'
        verbose_name = _('Health Category Threshold')
        verbose_name_plural = _('Health Category Thresholds')


class AQICategoryThreshold(models.Model):
    abbreviation = models.CharField(_("Abbrevation"), max_length=2)
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
    aqi_organization = models.ForeignKey(
        AQIOrganization, verbose_name=_("AQI Organization"),
        related_name=_("aqi_category_thresholds"),
        on_delete=models.DO_NOTHING, null=True, blank=True)
    pollutant = models.CharField(
        _("Pollutant"), max_length=15, default="sp_AQI")

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'aqi_category_threshold'
        verbose_name = _('AQI Category Threshold')
        verbose_name_plural = _('AQI Category Thresholds')
