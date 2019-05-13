from django.contrib import admin as reg_admin
from django.contrib.gis import admin
from .models import WorldBorder, Fire, TrafficFlow, TrafficStation


class WorldBorderAdmin(admin.GeoModelAdmin):
    list_display = ('name', 'un', 'region', 'subregion')
    list_filter = ('name', 'un', 'region', 'subregion')


class FireAdmin(admin.GeoModelAdmin):
    list_display = ('name', 'season', 'start_date', 'area_ha', 'districtid')
    list_filter = ('name', 'season', 'districtid')


class TrafficFlowAdmin(reg_admin.ModelAdmin):
    list_display = ('nb_scats_site', 'region_name', 'qt_interval_count',
                    'traffic_volume', )
    list_filter = ('nb_scats_site', 'region_name')


class TrafficStationAdmin(reg_admin.ModelAdmin):
    list_display = ('name', 'station_id', 'latitude', 'longitude', )


admin.site.register(Fire, FireAdmin)
admin.site.register(TrafficFlow, TrafficFlowAdmin)
admin.site.register(TrafficStation, TrafficStationAdmin)
admin.site.register(WorldBorder, WorldBorderAdmin)
