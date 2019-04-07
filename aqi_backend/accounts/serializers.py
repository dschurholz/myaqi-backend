from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    UserProfile, UserProfileQuestionnaireAnswer, PollutantSensitivity)

UserModel = get_user_model()


class PollutantSensitivitySerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source='get_level_display')

    class Meta:
        model = PollutantSensitivity
        fields = ('pollutant_id', 'level', 'level_display', )


class UserProfileQuestionnaireAnswerSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')

        # Perform the data validation.
        if not answer_id:
            raise serializers.ValidationError({
                'answer_id': 'This field is required.'
            })

        # Return the validated values. This will be available as
        # the `.validated_data` property.
        return {
            'question_id': question_id,
            'answer_id': answer_id
        }

    class Meta:
        model = UserProfileQuestionnaireAnswer
        fields = ('question_id', 'answer_id', )


class UserProfileSerializer(serializers.ModelSerializer):
    questionnaire_answers = UserProfileQuestionnaireAnswerSerializer(
        required=False, many=True)

    sensitivity_levels = PollutantSensitivitySerializer(
        many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            'age', 'colour_blindness', 'aqi_scale', 'modified',
            'questionnaire_answers', 'sensitivity_levels', )
        read_only_fields = ('modified', )

    def update(self, instance, validated_data):
        questionnaire_answers = validated_data.pop(
            'questionnaire_answers', [])
        answers_changed = instance.answers_will_change(
            questionnaire_answers)
        for a in questionnaire_answers:
            UserProfileQuestionnaireAnswer.objects.update_or_create(
                profile=instance, question_id=a['question_id'], defaults={
                    'answer_id': a['answer_id']
                })

        # Update sensitivity levels
        if answers_changed:
            instance.update_sensitivity_levels()
        return super(UserProfileSerializer, self).update(
            instance, validated_data)


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
        questionnaire_answers = profile.pop(
            'questionnaire_answers', [])
        if profile is not None:
            upProfile, created = UserProfile.objects.update_or_create(
                user=instance, defaults=profile)
            answers_changed = upProfile.answers_will_change(
                questionnaire_answers)
            for a in questionnaire_answers:
                UserProfileQuestionnaireAnswer.objects.update_or_create(
                    profile=upProfile, question_id=a['question_id'], defaults={
                        'answer_id': a['answer_id']
                    })

            # Update sensitivity levels
            if answers_changed:
                upProfile.update_sensitivity_levels()
        return super(ExtendedUserSerializer, self).update(
            instance, validated_data)
