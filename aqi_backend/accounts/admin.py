from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from collections import OrderedDict

from .constants import AQI_SCALES
from .models import UserProfile

UserModel = get_user_model()


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 1


class ExtendedUserAdmin(UserAdmin):
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
