from rest_framework import serializers

from .models import (
    AQIOrganization,
    AQICategoryThreshold,
    HealthCategoryThreshold
)


class AQICategoryThresholdSerializer(serializers.ModelSerializer):

    class Meta:
        model = AQICategoryThreshold
        fields = (
            'abbreviation', 'lower_threshold_value', 'upper_threshold_value',
            'description', 'background_colour', 'foreground_colour',
            'aqi_organization_id', 'pollutant')
        read_only_fields = fields


class HealthCategoryThresholdSerializer(serializers.ModelSerializer):

    class Meta:
        model = HealthCategoryThreshold
        fields = (
            'level', 'threshold_value', 'description', 'value_range',
            'visibility', 'message', 'background_colour', 'foreground_colour',
            'aqi_organization_id', 'pollutant')
        read_only_fields = fields


class AQIOrganizationSerializer(serializers.ModelSerializer):
    health_category_thresholds = HealthCategoryThresholdSerializer(many=True)
    aqi_category_thresholds = AQICategoryThresholdSerializer(many=True)

    class Meta:
        model = AQIOrganization
        fields = (
            'abbreviation', 'name', 'description', 'logo',
            'health_category_thresholds', 'aqi_category_thresholds', )
        read_only_fields = fields
