from django.contrib import admin

from .models import (
    AtmosphericPressureHourly,
    COHourly,
    HumidityHourly,
    NO2Hourly,
    O3Hourly,
    Pm10Hourly,
    Pm25Hourly,
    SO2Hourly,
    TemparatureHourly,
    WindHourly,
)


class GeneralAdmin(admin.ModelAdmin):
    list_display = (
        'sample_measurement', 'date_local', 'time_local', 'units_of_measure',
        'parameter_name', 'state_name', 'county_name', 'site_num', )
    list_filter = (
        'date_local', 'state_name', 'county_name', 'site_num', )


admin.site.register(AtmosphericPressureHourly, GeneralAdmin)
admin.site.register(COHourly, GeneralAdmin)
admin.site.register(HumidityHourly, GeneralAdmin)
admin.site.register(NO2Hourly, GeneralAdmin)
admin.site.register(O3Hourly, GeneralAdmin)
admin.site.register(Pm10Hourly, GeneralAdmin)
admin.site.register(Pm25Hourly, GeneralAdmin)
admin.site.register(SO2Hourly, GeneralAdmin)
admin.site.register(TemparatureHourly, GeneralAdmin)
admin.site.register(WindHourly, GeneralAdmin)
