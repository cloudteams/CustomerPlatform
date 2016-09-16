from django.contrib.postgres.fields import ArrayField
from django.db.models import *
from gamification.lists import *
from activitytracker.models import *


class XPRule(Model):
    """
    A rule that rewards or punishes with an amount of XP points on a certain event
    """
    event = CharField(max_length=255, choices=XP_EVENTS)
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


class Badge(Model):
    """
    A badge, probably with some level variations
    """
    name = CharField(max_length=255)
    slogan = CharField(max_length=255)
    rule = CharField(max_length=255, choices=BADGE_RULES)
    active = BooleanField(default=True)
    levels = ArrayField(base_field=SmallIntegerField())

    def get_description(self, level=0):
        title = self.get_rule_display()

        # the title may contain a counter based on
        title = title.replace('-X-', str(self.levels[level]))

        return title

    def __str__(self):
        return 'Badge #%d: %s - %s' % (self.pk, self.name, self.get_rule_display())


class BadgeReward(Model):
    """
    A badge was awarded to a user (optionally at a certain level)
    """
    user = ForeignKey(User)
    badge = ForeignKey(Badge)
    level = SmallIntegerField(default=0)
    created = DateTimeField(auto_now_add=True)


class GamificationProfile(Model):
    """
    Gamification information of a specific user
    """
    user = ForeignKey(User)
    xp_points = IntegerField(default=0)
    number_of_badges = IntegerField(default=0)

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
    def badges(self):
        return self.user

    def xp_leaderboard(self):
        around = 5  # users over and below self
        leaders = GamificationProfile.objects.values_list('id', flat=True).order_by('-xp_points')

        # first pass - find user's position
        for idx, gp_id in enumerate(leaders):
            if gp_id == self.pk:
                pos = idx
                break

        # fetch profiles
        start_pos = pos - around
        if start_pos < 0:
            start_pos = 0
        end_pos = pos + around + 1

        leader_profiles = GamificationProfile.objects.all().order_by('-xp_points')[start_pos:end_pos]

        # second pass - add profiles
        for idx, gp in enumerate(leader_profiles):
            gp.ranking = start_pos + idx + 1  # one based

        return leader_profiles

    def __str__(self):
        return '%s: %d XP, %d badges' % (self.user.username, self.xp_points, self.number_of_badges)


@property
def gamification_profile(self):
    try:
        return self._gamification_profile
    except AttributeError:
        self._gamification_profile = GamificationProfile.objects.get_or_create(user=self)[0]
        return self._gamification_profile

User.gamification_profile = gamification_profile
