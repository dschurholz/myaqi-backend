from rest_framework import serializers

from .models import (
    AQIOrganization,
    AQICategoryThreshold,
    HealthCategoryThreshold,
    Pollutant,
    ProfileQuestion,
    ProfileQuestionAnswer,
    ProfileAnswerPollutantIndex
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


class PollutantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pollutant
        fields = ('abbreviation', 'name', )
        read_only_fields = fields


class ProfileAnswerPollutantIndexSerializer(serializers.ModelSerializer):
    pollutant = PollutantSerializer()

    class Meta:
        model = ProfileAnswerPollutantIndex
        fields = ('id', 'index', 'pollutant', )
        read_only_fields = fields


class ProfileQuestionAnswerSerializer(serializers.ModelSerializer):
    indexes = ProfileAnswerPollutantIndexSerializer(many=True)

    class Meta:
        model = ProfileQuestionAnswer
        fields = ('id', 'order', 'text', 'indexes', )
        read_only_fields = fields


class ProfileQuestionSerializer(serializers.ModelSerializer):
    answers = ProfileQuestionAnswerSerializer(many=True)

    class Meta:
        model = ProfileQuestion
        fields = ('id', 'order', 'text', 'active', 'answers', )
        read_only_fields = fields
