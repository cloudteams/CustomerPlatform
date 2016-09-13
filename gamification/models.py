from django.db.models import *
from gamification.lists import *
from activitytracker.models import *


class XPRule(Model):
    """
    A rule that rewards or punishes with an amount of XP points on a certain event
    """
    event = CharField(max_length=255, choices=EVENTS)
    recurring = BooleanField(default=True)
    reward = IntegerField()
    active = BooleanField(default=True)


class XPRuleApplication(Model):
    """
    A rule was applied for a user
    """
    user = ForeignKey(User)
    rule = ForeignKey(XPRule)
    created = DateTimeField(auto_now_add=True)


class GamificationProfile(Model):
    """
    Gamification information of a specific user
    """
    user = ForeignKey(User)
    xp_points = IntegerField(default=0)


@property
def gamification_profile(self):
    try:
        return self._gamification_profile
    except AttributeError:
        self.gamification_profile = GamificationProfile.objects.get_or_create(user=self)[0]
        return self.gamification_profile

User.gamification_profile = gamification_profile
