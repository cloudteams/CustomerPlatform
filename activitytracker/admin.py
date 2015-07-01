from django.contrib import admin

from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name')


class PerformsAdmin(admin.ModelAdmin):
    list_display = ('activity__activity_name', 'first_name', 'last_name')


class ActivityAdmin(admin.ModelAdmin):
    list_display = ('activity_name', 'icon_classname')


class PerformsProviderInfoAdmin(admin.ModelAdmin):
    list_display = ('instance', 'provider', 'provider_instance_id')

class PerformsAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity', 'location_lat', 'location_lng')


admin.site.register(User, UserAdmin)
admin.site.register(PerformsProviderInfo,PerformsProviderInfoAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Performs,PerformsAdmin)
admin.site.register(Friend)
admin.site.register(Object)
admin.site.register(Places)
admin.site.register(UserVerification)


