from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
import nested_admin

from .models import (
    UserProfile, UserProfileQuestionnaireAnswer, PollutantSensitivity)

UserModel = get_user_model()


class PollutantSensitivityInline(nested_admin.NestedStackedInline):
    model = PollutantSensitivity
    extra = 0


class UserProfileQuestionnaireAnswerInline(nested_admin.NestedStackedInline):
    model = UserProfileQuestionnaireAnswer
    extra = 0


class UserProfileInline(nested_admin.NestedStackedInline):
    model = UserProfile
    extra = 0
    inlines = (
        UserProfileQuestionnaireAnswerInline, PollutantSensitivityInline)


class ExtendedUserAdmin(nested_admin.NestedModelAdmin, UserAdmin):
    inlines = (UserProfileInline, )
    list_display = (UserAdmin.list_display + (
        'get_age', 'get_colour_blindness', 'get_aqi_scale'))

    def get_age(self, obj):
        return obj.profile.age
    get_age.short_description = 'Age'
    get_age.admin_order_field = 'profile__age'

    def get_colour_blindness(self, obj):
        return obj.profile.colour_blindness
    get_colour_blindness.short_description = 'Colour Blindness'
    get_colour_blindness.admin_order_field = 'profile__colour_blindness'
    get_colour_blindness.boolean = True

    def get_aqi_scale(self, obj):
        return obj.profile.aqi_scale
    get_aqi_scale.short_description = 'Preferred AQI Scale'
    get_aqi_scale.admin_order_field = 'profile__aqi_scale'


admin.site.unregister(UserModel)
admin.site.register(UserModel, ExtendedUserAdmin)
