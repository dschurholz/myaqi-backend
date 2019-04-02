from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import UserProfile

UserModel = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('age', 'colour_blindness', 'aqi_scale', 'modified', )
        read_only_fields = ('modified', )


class UserSerializer(serializers.HyperlinkedModelSerializer):

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = UserModel
        fields = (
            'id', 'url', 'username', 'email', 'password', 'first_name',
            'last_name')
        extra_kwargs = {
            'url': {
                'view_name': 'api:accounts:user-detail'
            },
            'password': {'write_only': True}
        }


class ExtendedUserSerializer(UserSerializer):

    profile = UserProfileSerializer(required=False)

    class Meta(UserSerializer.Meta):
        fields = (
            'id', 'url', 'username', 'email', 'first_name',
            'last_name', 'profile', 'is_staff', 'is_active',
            'is_superuser', 'date_joined', )
        read_only_fields = (
            'is_staff', 'is_superuser', 'is_active', 'date_joined', )

    def update(self, instance, validated_data):
        profile = validated_data.pop('profile', None)
        if profile is not None:
            UserProfile.objects.update_or_create(
                user=instance, defaults=profile)
        return super(ExtendedUserSerializer, self).update(
            instance, validated_data)
