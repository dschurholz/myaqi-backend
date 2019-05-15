from django.utils.translation import ugettext_lazy as _
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.safestring import mark_safe


class AQIOrganization(models.Model):
    abbreviation = models.CharField(
        _("Abbrevation"), primary_key=True, max_length=5)
    name = models.CharField(
        _("Name"), max_length=127, blank=True, null=True)
    description = RichTextField(_("Description"), blank=True, null=True)
    logo = models.URLField(_("Logo"), blank=True, null=True)

    def logo_tag(self):
        return mark_safe(u'<img height="50px" src="{0}" />'.format(self.logo))
    logo_tag.short_description = 'Logo'

    def __str__(self):
        return self.abbreviation

    def get_categories(self, values, pollutant):
        if self.abbreviation == 'AUEPA':
            aqi_cats = self.aqi_category_thresholds.filter(
                pollutant=pollutant,
                lower_threshold_value__isnull=False).order_by(
                    'lower_threshold_value')

            def get_cat(val):
                for cat in aqi_cats:
                    if val < cat.upper_threshold_value:
                        return cat.abbreviation

            return map(get_cat, values)
        return None

    class Meta:
        db_table = 'aqi_organization'
        verbose_name = _('AQI Organization')
        verbose_name_plural = _('AQI Organizations')


class HealthCategoryThreshold(models.Model):
    level = models.PositiveSmallIntegerField(_("Level"), primary_key=True)
    threshold_value = models.FloatField(
        _("Threshold Value"), blank=True, null=True)
    description = models.CharField(
        _("Description"), max_length=63, blank=True, null=True)
    value_range = models.CharField(
        _("Value Range"), max_length=63, blank=True, null=True)
    visibility = models.CharField(
        _("Visibility"), max_length=63, blank=True, null=True)
    message = RichTextField(_("Message"), blank=True, null=True)
    background_colour = models.CharField(
        _("Background Colour"), max_length=7, blank=True, null=True)
    foreground_colour = models.CharField(
        _("Foreground Colour"), max_length=7, blank=True, null=True)
    aqi_organization = models.ForeignKey(
        AQIOrganization, verbose_name=_("AQI Organization"),
        related_name=_("health_category_thresholds"),
        on_delete=models.DO_NOTHING, null=True, blank=True)
    pollutant = models.CharField(
        _("Pollutant"), max_length=15, default="sp_AQI")

    def __str__(self):
        return "{0}-{1}".format(self.level, self.description)

    class Meta:
        db_table = 'health_category_threshold'
        verbose_name = _('Health Category Threshold')
        verbose_name_plural = _('Health Category Thresholds')


class AQICategoryThreshold(models.Model):
    UG_M3 = 'ug/m3'
    PPM = 'ppm'
    PPB = 'ppb'
    NU = '-'
    UNITS = (
        (NU, 'no units'),
        (UG_M3, 'micro-gram per cubic meter'),
        (PPM, 'parts per million'),
        (PPB, 'parts per billion'),
    )
    abbreviation = models.CharField(_("Abbrevation"), max_length=2)
    lower_threshold_value = models.FloatField(
        _("Lower Threshold Value"), blank=True, null=True)
    upper_threshold_value = models.FloatField(
        _("Upper Threshold Value"), blank=True, null=True)
    description = models.CharField(
        _("Description"), max_length=63, blank=True, null=True)
    background_colour = models.CharField(
        _("Background Colour"), max_length=7, blank=True, null=True)
    foreground_colour = models.CharField(
        _("Foreground Colour"), max_length=7, blank=True, null=True)
    aqi_organization = models.ForeignKey(
        AQIOrganization, verbose_name=_("AQI Organization"),
        related_name=_("aqi_category_thresholds"),
        on_delete=models.DO_NOTHING, null=True, blank=True)
    pollutant = models.CharField(
        _("Pollutant"), max_length=15, default="aqi")
    units = models.CharField(
        _("Units"), max_length=12, choices=UNITS, default=NU)

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'aqi_category_threshold'
        verbose_name = _('AQI Category Threshold')
        verbose_name_plural = _('AQI Category Thresholds')


class Pollutant(models.Model):
    abbreviation = models.CharField(
        _("Abbrevation"), primary_key=True, max_length=5)
    name = models.CharField(
        _("Name"), max_length=63, blank=True, null=True)

    def __str__(self):
        return self.abbreviation

    class Meta:
        db_table = 'pollutant'
        verbose_name = _('Pollutant')
        verbose_name_plural = _('Pollutants')


class ProfileQuestion(models.Model):
    order = models.PositiveSmallIntegerField(
        _('Order'), unique=True, null=True, blank=True)
    text = RichTextField(_('Question Text'))
    active = models.BooleanField(_('Is Active'), default=True)

    def __str__(self):
        return 'Question {}'.format(self.order)

    def save(self, *args, **kwargs):
        if self.order is None:
            self.order = ProfileQuestion.objects.all().order_by(
                '-order').first()
            if self.order is None:
                self.order = 1

        super(ProfileQuestion, self).save(*args, **kwargs)

    class Meta:
        db_table = 'profile_question'
        verbose_name = _('Profile Question')
        verbose_name_plural = _('Profile Questions')
        ordering = ('order', )


class ProfileQuestionAnswer(models.Model):
    text = RichTextField(_('Answer Text'))
    order = models.PositiveSmallIntegerField(_('Order'), null=True, blank=True)
    question = models.ForeignKey(
        ProfileQuestion, verbose_name=_('Profile Question'),
        related_name='answers', on_delete=models.CASCADE)

    def __str__(self):
        return 'Answer {0}-{1}'.format(self.question.order, self.order)

    def save(self, *args, **kwargs):
        if self.order is None:
            self.order = ProfileQuestionAnswer.objects.all().order_by(
                '-order').first()
            if self.order is None:
                self.order = 1

        super(ProfileQuestionAnswer, self).save(*args, **kwargs)

    class Meta:
        db_table = 'profile_q_answer'
        verbose_name = _('Profile Question Answer')
        verbose_name_plural = _('Profile Question Answers')
        ordering = ('question__order', 'order', )
        unique_together = ('question', 'order')


class ProfileAnswerPollutantIndex(models.Model):
    pollutant = models.ForeignKey(
        Pollutant, verbose_name=_('Pollutant'), related_name='indexes',
        on_delete=models.CASCADE)
    answer = models.ForeignKey(
        ProfileQuestionAnswer, verbose_name=_('Answer'),
        related_name='indexes', on_delete=models.CASCADE)
    index = models.FloatField(_('Health Influence Index'), default=0.0)

    def __str__(self):
        return 'Index {0}-{1}-{2}'.format(
            self.answer.question.order, self.answer.order, self.pollutant)
