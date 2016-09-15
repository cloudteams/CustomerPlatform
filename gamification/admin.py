from django.contrib import admin
from gamification.models import *


class XPRuleAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'event', 'reward', 'recurring', 'active']


class XPRuleApplicationAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']
    list_display = ['user', 'rule', 'created']


class BadgeAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'rule', 'levels', 'active']


class BadgeRewardAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']
    list_display = ['user', 'badge', 'level', 'created']


class GamificationProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']
    list_display = ['user', 'xp_points', 'number_of_badges']


admin.site.register(XPRule, XPRuleAdmin)
admin.site.register(XPRuleApplication, XPRuleApplicationAdmin)
admin.site.register(Badge, BadgeAdmin)
admin.site.register(BadgeReward, BadgeRewardAdmin)
admin.site.register(GamificationProfile, GamificationProfileAdmin)
