from rest_framework import serializers

from .models import (
    Site,
    SiteList,
    IncidentSite,
    EquipmentType,
    Monitor,
    TimeBasis,
    MonitorTimeBasis
)


class IncidentSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentSite
        fields = ('emv_url', 'incident_icon', )
        read_only_fields = ('emv_url', 'incident_icon', )


class SiteListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteList
        fields = ('name', )
        read_only_fields = ('name', )


class ShortSiteSerializer(serializers.HyperlinkedModelSerializer):
    site_list = SiteListSerializer(many=True, read_only=True)

    class Meta:
        model = Site
        fields = (
            'site_id', 'url', 'name', 'is_station_offline', 'site_list', )
        read_only_fields = (
            'site_id', 'url', 'name', 'is_station_offline', 'site_list', )
        extra_kwargs = {
            'url': {
                'view_name': 'api:au-epa-data:site-detail'
            }
        }


class SiteSerializer(ShortSiteSerializer):
    incidents = SiteListSerializer(many=True, read_only=True)

    class Meta(ShortSiteSerializer.Meta):
        fields = (
            'site_id', 'url', 'name', 'latitude', 'longitude',
            'fire_hazard_category', 'is_station_offline', 'has_incident',
            'incident_type', 'incidents', 'site_list', )
        read_only_fields = (
            'site_id', 'url', 'name', 'latitude', 'longitude',
            'fire_hazard_category', 'is_station_offline', 'has_incident',
            'incident_type', )
        extra_kwargs = {
            'url': {
                'view_name': 'api:au-epa-data:site-detail'
            }
        }


class EquipmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentType
        fields = ('id_number', 'code', 'description', )
        read_only_fields = ('id_number', 'code', 'description', )


class TimeBasisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeBasis
        fields = (
            'time_base_id', 'description', 'is_rolling_average',
            'rolling_average_period', 'min_data_percent',
            'time_basis_desc_url')
        read_only_fields = (
            'time_base_id', 'description', 'is_rolling_average',
            'rolling_average_period', 'min_data_percent',
            'time_basis_desc_url')


class MonitorTimeBasisSerializer(serializers.ModelSerializer):
    time_basis = TimeBasisSerializer(read_only=True)

    class Meta:
        model = MonitorTimeBasis
        fields = (
            'time_basis', 'aqi_pollutant_standard', 'incident_type',
            'presentation_order', 'calc_aqi', 'calc_health_category')
        read_only_fields = (
            'time_basis', 'aqi_pollutant_standard', 'incident_type',
            'presentation_order', 'calc_aqi', 'calc_health_category')


class MonitorSerializer(serializers.HyperlinkedModelSerializer):
    equipment_type = EquipmentTypeSerializer(read_only=True)
    monitor_time_basis = MonitorTimeBasisSerializer(many=True, read_only=True)

    class Meta:
        model = Monitor
        fields = (
            'monitor_id', 'url', 'short_name', 'common_name',
            'epa_description_url', 'unit_of_measure', 'presentation_precision',
            'equipment_type', 'monitor_time_basis')
        read_only_fields = (
            'monitor_id', 'url', 'short_name', 'common_name',
            'epa_description_url', 'unit_of_measure', 'presentation_precision')
        extra_kwargs = {
            'url': {
                'view_name': 'api:au-epa-data:monitor-detail',
                'lookup_field': 'slug'
            }
        }


class ExtendedMonitorSerializer(MonitorSerializer):
    sites = ShortSiteSerializer(many=True, read_only=True)

    class Meta(MonitorSerializer.Meta):
        fields = (
            'monitor_id', 'url', 'short_name', 'common_name',
            'epa_description_url', 'unit_of_measure', 'presentation_precision',
            'equipment_type', 'sites', )
        read_only_fields = (
            'monitor_id', 'url', 'short_name', 'common_name',
            'epa_description_url', 'unit_of_measure', 'presentation_precision')


class ExtendedSiteSerializer(SiteSerializer):
    monitors = MonitorSerializer(many=True, read_only=True)

    class Meta(SiteSerializer.Meta):
        fields = (
            'site_id', 'url', 'name', 'latitude', 'longitude',
            'fire_hazard_category', 'is_station_offline', 'has_incident',
            'incident_type', 'incidents', 'site_list', 'monitors', )
        read_only_fields = (
            'site_id', 'url', 'name', 'latitude', 'longitude',
            'fire_hazard_category', 'is_station_offline', 'has_incident',
            'incident_type', 'monitors', )
        extra_kwargs = {
            'url': {
                'view_name': 'api:au-epa-data:site-detail'
            }
        }
