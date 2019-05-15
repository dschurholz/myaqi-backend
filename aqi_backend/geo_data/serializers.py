import json
from rest_framework import serializers
from django.core.serializers import serialize

from .models import Fire, TrafficFlow, TrafficStation


class FireSerializer(serializers.ModelSerializer):
    geom = serializers.SerializerMethodField(
        read_only=True, method_name='serialize_geometry')

    def serialize_geometry(self, obj):
        geom = serialize(
            'geojson', [obj], geometry_field='geom', fields=('id', ))
        return json.loads(geom)['features'][0]['geometry']

    class Meta:
        model = Fire
        fields = '__all__'


class TrafficFlowSerializer(serializers.ModelSerializer):

    class Meta:
        model = TrafficFlow
        fields = '__all__'


class TrafficStationSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField(
        read_only=True, method_name='serialize_geometry')

    quantiles = serializers.ListField(
        child=serializers.IntegerField()
    )

    max_volume = serializers.IntegerField()

    avg_volume = serializers.FloatField()

    def serialize_geometry(self, obj):
        path = serialize(
            'geojson', [obj], geometry_field='path', fields=('id', ))
        return json.loads(path)['features'][0]['geometry']

    class Meta:
        model = TrafficStation
        fields = '__all__'
