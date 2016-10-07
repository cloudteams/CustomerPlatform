from django.db.models.signals import post_delete

from activitytracker.views import visited_activity_tracker_home
from gamification.models import *

from ct_projects.models import *
from profile.models import *

from django.db import transaction
from logging import warn


def apply_badge_rule(user, badge_rule, counter):
    """
    Generic routine that applies badge updates
    :param user: The user to be rewarded or stripped from the badge
    :param badge_rule: The rule that must be checked
    :param counter: A counter that specifies the level that should be awarded
    :return:
    """
    # get badge by rule
    try:
        badge = Badge.objects.get(rule=badge_rule)
    except XPRule.DoesNotExist:
        warn('Badge for rule %s does not exist' % badge_rule)
        return

    # ignore disabled rules
    if not badge.active:
        return

    # find the appropriate level
    award = -1
    for idx, level in enumerate(badge.levels):
        if counter >= level:
            award = idx

    with transaction.atomic():
        num_diff = 0
        diff = 0
        del_badge = None
        if award >= 0:  # has badge
            try:
                br = BadgeReward.objects.get(user_id=user.pk, badge_id=badge.pk)
                if br.level != award:
                    # upgrade or downgrade?
                    if br.level < award:
                        diff = +1
                    else:
                        diff = -1

                    # save the change
                    br.level = award
                    br.save()
            except BadgeReward.DoesNotExist:
                num_diff = +1
                # definitely an upgrade
                diff = +1
                # crete the reward
                br = BadgeReward.objects.create(user_id=user.pk, badge_id=badge.pk, level=0)
        else:  # doesn't have badge
            try:
                br = BadgeReward.objects.get(user_id=user.pk, badge_id=badge.pk)
                del_badge = badge

                # delete the reward
                br.delete()
                num_diff = -1

                # definitely a downgrade
                diff = -1
            except BadgeReward.DoesNotExist:
                # nothing changed
                pass

        # if there's any change in the number of budges, update the gamification profile of the user
        if num_diff != 0:
            gp = user.gamification_profile
            gp.number_of_badges += num_diff
            gp.save()

        # if there's any change in the budges, send a notification
        if diff != 0:
            if diff >= 0:
                if br.level == 0:
                    message = '[P]<p>New badge!</p><p><b>%s</b>: %s</p>' % \
                              (br.badge.name, br.badge.get_description(level=br.level))
                else:
                    message = '[P]<p>Badge upgraded to %s!</p><p><b>%s</b>: %s</p>' % \
                              (br.badge.name, BADGE_LEVELS[br.level], br.badge.get_description(level=br.level))
            else:
                if del_badge:
                    message = '[N]Lost badge %s...' % del_badge.name
                else:
                    message = '[P]Badge %s downgraded to %s...<br />' % (br.badge.name, BADGE_LEVELS[br.level])

            Notification.objects.create(user=user, text=message, persistent=False)

# register events

# RULE BR1 #


def on_project_following_change(user):
    apply_badge_rule(user, 'PROJECT_FOLLOW', counter=user.follows.count())


@receiver(post_save, sender=ProjectFollowing)
def on_project_following_create(sender, instance, created, **kwargs):
    if created:
        on_project_following_change(instance.user)


@receiver(post_delete, sender=ProjectFollowing)
def on_project_following_delete(sender, instance, **kwargs):
    on_project_following_change(instance.user)

# RULE BR2 #


def on_connected_services_change(user):
    apply_badge_rule(user, 'CONNECT_SERVICE', counter=UserSocialAuth.objects.filter(user_id=user.pk).count())


@receiver(post_save, sender=UserSocialAuth)
def on_activity_tracker_service_add(sender, instance, created, **kwargs):
    if created:
        on_connected_services_change(instance.user)


@receiver(post_delete, sender=UserSocialAuth)
def on_activity_tracker_service_remove(sender, instance, **kwargs):
    on_connected_services_change(instance.user)

# RULE BR3 #


@receiver(platform_invitation_accepted, sender=PlatformInvitation)
def on_platform_invitation_accepted(sender, invitation, **kwargs):
    counter = PlatformInvitation.objects.filter(user=invitation.user, status='ACCEPTED').count()
    apply_badge_rule(invitation.user, 'INVITATION_ACCEPTED', counter=counter)


# RULE BR12 #


@receiver(post_save, sender=UserProfile)
def on_user_profile_updated(sender, instance, created, **kwargs):
    if instance.get_completion_progress() == 100:
        counter = 1
    else:
        counter = 0

    apply_badge_rule(instance.user, 'PROFILE_COMPLETE', counter=counter)


@receiver(post_save, sender=Influence)
@receiver(post_save, sender=DeviceUsage)
@receiver(post_save, sender=PlatformUsage)
@receiver(post_save, sender=UserBrandOpinion)
@receiver(post_delete, sender=Influence)
@receiver(post_delete, sender=DeviceUsage)
@receiver(post_delete, sender=PlatformUsage)
@receiver(post_delete, sender=UserBrandOpinion)
def on_user_profile_m2m_updated(sender, instance, **kwargs):
    if instance.user.profile.get_completion_progress() == 100:
        counter = 1
    else:
        counter = 0

    apply_badge_rule(instance.user, 'PROFILE_COMPLETE', counter=counter)

