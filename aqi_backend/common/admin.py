from django.contrib import admin

from .models import (
    AQICategoryThreshold,
    AQIOrganization,
    HealthCategoryThreshold
)


class AQIOrganizationAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name', 'description', 'logo_tag', )
    readonly_fields = ('logo_tag',)


class HealthCategoryThresholdAdmin(admin.ModelAdmin):
    list_display = (
        'level', 'aqi_organization', 'threshold_value', 'description',
        'value_range', 'visibility', 'message', 'background_colour',
        'foreground_colour', 'pollutant', )
    list_filter = ('aqi_organization', 'pollutant', )


class AQICategoryThresholdAdmin(admin.ModelAdmin):
    list_display = (
        'abbreviation', 'aqi_organization', 'lower_threshold_value',
        'upper_threshold_value', 'description', 'background_colour',
        'foreground_colour', 'pollutant', )
    list_filter = ('aqi_organization', 'pollutant', )


admin.site.register(AQIOrganization, AQIOrganizationAdmin)
admin.site.register(HealthCategoryThreshold, HealthCategoryThresholdAdmin)
admin.site.register(AQICategoryThreshold, AQICategoryThresholdAdmin)
