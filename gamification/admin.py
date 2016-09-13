from django.contrib import admin
from gamification.models import *


class XPRuleAdmin(admin.ModelAdmin):
    pass


class GamificationProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']


admin.site.register(XPRule, XPRuleAdmin)
admin.site.register(GamificationProfile, GamificationProfileAdmin)
