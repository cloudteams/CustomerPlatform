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

    def __str__(self):
        return 'XP Rule #%d - %s' % (self.pk, self.event)


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
    def next_level_points(self):
        return 1000

    @property
    def level(self):
        return int(math.ceil(self.xp_points / self.next_level_points)) + 1

    @property
    def extra_points(self):
        return self.xp_points % self.next_level_points

    @property
    def progress_to_next_level(self):
        return round((self.extra_points + 0.0) / self.next_level_points, 4)


@property
def gamification_profile(self):
    try:
        return self._gamification_profile
    except AttributeError:
        self._gamification_profile = GamificationProfile.objects.get_or_create(user=self)[0]
        return self._gamification_profile

User.gamification_profile = gamification_profile
