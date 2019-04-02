from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth import get_user_model

from .constants import AQI_SCALES, AU_EPA_AQI

from common.models import AQIOrganization

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

    class Meta:
        db_table = 'user_profile'
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
