import nested_admin
from django.contrib import admin

from .models import (
    AQICategoryThreshold,
    AQIOrganization,
    HealthCategoryThreshold,
    Pollutant,
    ProfileQuestion,
    ProfileQuestionAnswer,
    ProfileAnswerPollutantIndex
)


class AQIOrganizationAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name', 'description', 'logo_tag', )
    readonly_fields = ('logo_tag',)


class HealthCategoryThresholdAdmin(admin.ModelAdmin):
    list_display = (
        'level', 'aqi_organization', 'threshold_value', 'description',
        'value_range', 'visibility', 'message', 'background_colour',
        'foreground_colour', 'pollutant', )
    list_filter = ('aqi_organization', 'pollutant', )


class AQICategoryThresholdAdmin(admin.ModelAdmin):
    list_display = (
        'abbreviation', 'aqi_organization', 'lower_threshold_value',
        'upper_threshold_value', 'description', 'background_colour',
        'foreground_colour', 'pollutant', )
    list_filter = ('aqi_organization', 'pollutant', )


class PollutantAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'name', )


class ProfileAnswerPollutantIndexInline(nested_admin.NestedStackedInline):
    model = ProfileAnswerPollutantIndex
    extra = 0


class ProfileQuestionAnswerInline(nested_admin.NestedStackedInline):
    model = ProfileQuestionAnswer
    extra = 0
    inlines = (ProfileAnswerPollutantIndexInline, )


class ProfileQuestionAdmin(nested_admin.NestedModelAdmin):
    inlines = (ProfileQuestionAnswerInline, )
    list_display = ('get_str', 'order', 'text', )

    def get_str(self, obj):
        return obj.__str__()
    get_str.short_description = 'Question'
    get_str.admin_order_field = 'order'


class ProfileQuestionAnswerAdmin(nested_admin.NestedModelAdmin):
    inlines = (ProfileAnswerPollutantIndexInline, )
    list_display = ('get_str', 'order', 'text', )

    def get_str(self, obj):
        return obj.__str__()
    get_str.short_description = 'Answer'
    get_str.admin_order_field = 'question__order'


admin.site.register(AQIOrganization, AQIOrganizationAdmin)
admin.site.register(HealthCategoryThreshold, HealthCategoryThresholdAdmin)
admin.site.register(AQICategoryThreshold, AQICategoryThresholdAdmin)
admin.site.register(Pollutant, PollutantAdmin)
admin.site.register(ProfileQuestion, ProfileQuestionAdmin)
admin.site.register(ProfileQuestionAnswer, ProfileQuestionAnswerAdmin)
