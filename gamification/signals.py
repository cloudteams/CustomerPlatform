from activitytracker.views import visited_activity_tracker_home
from gamification.models import *

from ct_projects.models import *
from profile.models import *

from django.db import transaction
from logging import warn


def apply_xp_rule(user, event):
    """
    Generic routine that applies XP Rules
    :param user: The user who will be rewarded
    :param event: The event that occurred
    :return:
    """
    # get rule by event
    try:
        rule = XPRule.objects.get(event=event)
    except XPRule.DoesNotExist:
        warn('Rule for event %s does not exist' % event)
        return

    # do not apply one time rules
    if not rule.recurring and XPRuleApplication.objects.filter(user_id=user.pk, rule_id=rule.pk).exists():
        return

    with transaction.atomic():
        # create the rule application object
        XPRuleApplication.objects.create(user_id=user.pk, rule_id=rule.pk)

        # update the gamification profile of the user
        gp = user.gamification_profile
        gp.xp_points += rule.reward
        gp.save()

        # create an on-the-fly notification
        message = '+%d XP points added to your profile!' % rule.reward
        Notification.objects.create(user=user, text=message, persistent=False)


# register events

@receiver(post_save, sender=User)
def on_user_signup(sender, instance, created, **kwargs):
    if created:
        apply_xp_rule(instance, 'SIGNUP')


@receiver(post_save, sender=UserSocialAuth)
def on_activity_tracker_service_add(sender, instance, created, **kwargs):
    if created:
        apply_xp_rule(instance.user, 'CONNECT_SERVICE')


@receiver(pre_delete, sender=UserSocialAuth)
def on_activity_tracker_service_remove(sender, instance, **kwargs):
    apply_xp_rule(instance.user, 'DISCONNECT_SERVICE')


@receiver(post_save, sender=Idea)
def on_idea_created(sender, instance, created, **kwargs):
    if created:
        apply_xp_rule(instance.user, 'NEW_IDEA')


@receiver(post_save, sender=ProjectFollowing)
def on_project_following_created(sender, instance, created, **kwargs):
    if created:
        apply_xp_rule(instance.user, 'PROJECT_FOLLOW')


@receiver(platform_invitation_accepted, sender=PlatformInvitation)
def on_platform_invitation_accepted(sender, invitation, **kwargs):
    apply_xp_rule(invitation.user, 'INVITATION_ACCEPTED')


@receiver(visited_activity_tracker_home, sender=User)
def on_visit_activity_tracker_home(sender, user, **kwargs):
    apply_xp_rule(user, 'OPEN_ACTIVITY_TRACKER')
