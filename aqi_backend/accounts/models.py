from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth import get_user_model

from common.models import (
    AQIOrganization,
    Pollutant,
    ProfileQuestion,
    ProfileQuestionAnswer,
    ProfileAnswerPollutantIndex
)
from .constants import (
    SENSITIVITY_LEVELS_IDS, SENSITIVITY_LEVELS, TEMP_POLLUTANT_TRANSLATION)

UserModel = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(
        UserModel, verbose_name=_('User'), related_name='profile',
        on_delete=models.CASCADE)
    age = models.PositiveSmallIntegerField(_('Age'), null=True, blank=True)
    colour_blindness = models.BooleanField(
        _('Colour Blindness'), default=False)
    aqi_scale = models.ForeignKey(
        AQIOrganization, verbose_name=_('Preferred AQI scale'),
        on_delete=models.DO_NOTHING, blank=True, null=True)
    modified = models.DateTimeField(_('Last Modified'), auto_now=True)

    def __str__(self):
        return '{0}\'s-{1}'.format(self.user.username, 'Profile')

    def answers_will_change(self, new_answers):
        old_answers = self.questionnaire_answers.all()
        if len(new_answers) != old_answers.count():
            return True
        for i, a in enumerate(new_answers):
            ans = old_answers.filter(
                question=a['question_id'],
                answer=a['answer_id'])
            if ans.count() == 0:
                return True
        return False

    def update_sensitivity_levels(self):
        pollutants = Pollutant.objects.all()
        for pollutant in pollutants:
            self.sensitivity_levels.update_or_create(
                pollutant=pollutant,
                defaults={
                    'level': self._update_sensitivity_levels(
                        TEMP_POLLUTANT_TRANSLATION[pollutant.pk])
                }
            )

    def _update_sensitivity_levels(self, pollutant):
        indexes_count = ProfileAnswerPollutantIndex.objects.filter(
            pollutant_id=pollutant,
            answer_id__in=self.questionnaire_answers.all().values_list(
                'answer_id', flat=True)).values(
                    'index').annotate(models.Count('index'))

        low_count = list(filter(
            lambda x: x['index'] == SENSITIVITY_LEVELS_IDS['LOW'],
            indexes_count
        ))
        low_count = low_count[0]['index__count'] if len(low_count) > 0 else 0
        moderate_count = list(filter(
            lambda x: x['index'] == SENSITIVITY_LEVELS_IDS['MODERATE'],
            indexes_count
        ))
        moderate_count = (
            moderate_count[0]['index__count'] if len(moderate_count) > 0 else 0
        )
        high_count = list(filter(
            lambda x: x['index'] == SENSITIVITY_LEVELS_IDS['HIGH'],
            indexes_count
        ))
        high_count = (
            high_count[0]['index__count'] if len(high_count) > 0 else 0)
        extreme_count = list(filter(
            lambda x: x['index'] == SENSITIVITY_LEVELS_IDS['EXTREMELY_HIGH'],
            indexes_count
        ))
        extreme_count = (
            extreme_count[0]['index__count'] if len(extreme_count) > 0 else 0
        )

        if extreme_count > 0:
            return SENSITIVITY_LEVELS_IDS['EXTREMELY_HIGH']
        if high_count > 3:
            return SENSITIVITY_LEVELS_IDS['EXTREMELY_HIGH']
        if high_count > 0 and high_count <= 3:
            return SENSITIVITY_LEVELS_IDS['HIGH']
        if moderate_count > 5:
            return SENSITIVITY_LEVELS_IDS['HIGH']
        if moderate_count > 0 and moderate_count <= 5:
            return SENSITIVITY_LEVELS_IDS['MODERATE']
        if low_count > 7:
            return SENSITIVITY_LEVELS_IDS['MODERATE']
        if low_count > 3 and low_count <= 7:
            return SENSITIVITY_LEVELS_IDS['LOW']
        return SENSITIVITY_LEVELS_IDS['NEUTRAL']

    class Meta:
        db_table = 'user_profile'
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')


class UserProfileQuestionnaireAnswer(models.Model):
    profile = models.ForeignKey(
        UserProfile, verbose_name=_('User Profile'),
        related_name='questionnaire_answers', on_delete=models.CASCADE)
    question = models.ForeignKey(
        ProfileQuestion, verbose_name=_('Question'),
        related_name='user_questionnaire_answers', on_delete=models.CASCADE,
        null=True, blank=True)
    answer = models.ForeignKey(
        ProfileQuestionAnswer, verbose_name=_('Answer'),
        related_name='user_questionnaire_answers', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.question is None and self.answer:
            self.question = self.answer.question

        super(UserProfileQuestionnaireAnswer, self).save(*args, **kwargs)

    def __str__(self):
        return "User {} has answer {} to question {}". format(
            self.profile.user, self.question, self.answer)

    class Meta:
        db_table = 'user_questionnaire_answer'
        verbose_name = _('User Questionnaire Answer')
        verbose_name_plural = _('User Questionnaire Answers')


class PollutantSensitivity(models.Model):
    profile = models.ForeignKey(
        UserProfile, verbose_name=_('User Profile'),
        related_name='sensitivity_levels', on_delete=models.CASCADE)
    pollutant = models.ForeignKey(
        Pollutant, verbose_name=_('Pollutant'),
        related_name='sensitivity_levels', on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField(
        _('Sensitivity Level'), choices=SENSITIVITY_LEVELS,
        default=SENSITIVITY_LEVELS_IDS['NEUTRAL'])

    def __str__(self):
        return "User {} has {} sensitiviy to pollutant {}". format(
            self.profile.user, self.get_level_display(), self.pollutant)

    class Meta:
        db_table = 'pollutant_sensitivity'
        verbose_name = _('Pollutant Sensitivity Level')
        verbose_name_plural = _('Pollutant Sensitivity Levels')
