from django.contrib import admin
from gamification.models import *


class XPRuleAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'event', 'reward', 'recurring', 'active']


class XPRuleApplicationAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']
    list_display = ['user', 'rule', 'created']


class GamificationProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']
    list_display = ['user', 'xp_points', ]


admin.site.register(XPRule, XPRuleAdmin)
admin.site.register(XPRuleApplication, XPRuleApplicationAdmin)
admin.site.register(GamificationProfile, GamificationProfileAdmin)
