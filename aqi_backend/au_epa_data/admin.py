from django.contrib import admin

from .models import (
    AQICategoryThreshold,
    EquipmentType,
    HealthCategoryThreshold,
    IncidentSite,
    Measurement,
    Monitor,
    MonitorTimeBasis,
    Site,
    SiteList,
    TimeBasis,
)


class IncidentSiteInline(admin.StackedInline):
    model = IncidentSite
    extra = 0


class SiteAdmin(admin.ModelAdmin):
    inlines = (IncidentSiteInline, )
    list_display = (
        'site_id', 'name', 'is_station_offline', 'has_incident', 'latitude',
        'longitude', )
    list_filter = (
        'is_station_offline', 'has_incident', )


class MonitorInline(admin.TabularInline):
    model = Monitor
    extra = 0
    readonly_fields = (
        'monitor_id', 'short_name', 'common_name', 'unit_of_measure',
        'presentation_precision', 'sites', 'epa_description_url')
    can_delete = False


class MonitorTimeBasisInline(admin.TabularInline):
    model = MonitorTimeBasis
    extra = 0


class EquipmentTypeAdmin(admin.ModelAdmin):
    inlines = (MonitorInline, )
    list_display = ('description', 'id_number', 'code')


class MonitorAdmin(admin.ModelAdmin):
    inlines = (MonitorTimeBasisInline, )
    list_display = (
        'monitor_id', 'short_name', 'common_name', 'unit_of_measure',
        'presentation_precision', )
    list_filter = (
        'sites', 'equipment_type', )


class TimeBasisAdmin(admin.ModelAdmin):
    inlines = (MonitorTimeBasisInline, )
    list_display = (
        'time_base_id', 'description', 'is_rolling_average',
        'rolling_average_period', 'min_data_percent', 'time_basis_desc_url')
    list_filter = ('sites', )


class HealthCategoryThresholdAdmin(admin.ModelAdmin):
    list_display = (
        'level', 'threshold_value', 'description', 'value_range',
        'visibility', 'message', 'background_colour', 'foreground_colour')


class AQICategoryThresholdAdmin(admin.ModelAdmin):
    list_display = (
        'abbreviation', 'lower_threshold_value', 'upper_threshold_value',
        'description', 'background_colour', 'foreground_colour')


class MeasurementAdmin(admin.ModelAdmin):
    list_display = (
        'date_time_start', 'site', 'monitor', 'time_basis', 'value',
        'quality_status', 'date_time_recorded', 'aqi_category_threshold',
        'health_category_threshold', )
    list_filter = (
        'site', 'monitor', 'time_basis', 'date_time_start',
        'aqi_category_threshold', 'health_category_threshold')


admin.site.register(Monitor, MonitorAdmin)
admin.site.register(EquipmentType, EquipmentTypeAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(SiteList)
admin.site.register(TimeBasis, TimeBasisAdmin)
admin.site.register(HealthCategoryThreshold, HealthCategoryThresholdAdmin)
admin.site.register(AQICategoryThreshold, AQICategoryThresholdAdmin)
admin.site.register(Measurement, MeasurementAdmin)
