from gamification.signals.badges import *


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

    # ignore disabled rules
    if not rule.active:
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
        if rule.reward >= 0:
            # check if level up
            if gp.extra_points < rule.reward:
                lvl_message = 'Level UP! You\'re now a level <b>#%d</b> customer!' % gp.level
            else:
                remaining_xp = gp.next_level_points - gp.extra_points % gp.next_level_points
                lvl_message = '%d more XP points for level %d' % (remaining_xp, gp.level + 1)
            message = '[P]+%d XP points added to your profile!<br />%s' % (rule.reward, lvl_message)
        else:
            message = '[N]-%d XP points lost from your profile...' % abs(rule.reward)

        Notification.objects.create(user=user, text=message, persistent=False)


# register events

# RULE XP1 #

@receiver(post_save, sender=User)
def on_user_signup(sender, instance, created, **kwargs):
    if created:
        apply_xp_rule(instance, 'SIGNUP')

# RULE XP2 #


@receiver(post_save, sender=UserProfile)
def on_user_profile_updated(sender, instance, created, **kwargs):
    if instance.get_completion_progress() == 100:
        apply_xp_rule(instance.user, 'PROFILE_COMPLETE')


@receiver(post_save, sender=Influence)
@receiver(post_save, sender=DeviceUsage)
@receiver(post_save, sender=PlatformUsage)
@receiver(post_save, sender=UserBrandOpinion)
def on_user_profile_m2m_updated(sender, instance, **kwargs):
    if instance.user.profile.get_completion_progress() == 100:
        apply_xp_rule(instance.user, 'PROFILE_COMPLETE')

# RULE XP3 #


@receiver(post_save, sender=UserSocialAuth)
def on_activity_tracker_service_add(sender, instance, created, **kwargs):
    if created:
        apply_xp_rule(instance.user, 'CONNECT_SERVICE')

# RULE XP4 #


@receiver(post_delete, sender=UserSocialAuth)
def on_activity_tracker_service_remove(sender, instance, **kwargs):
    apply_xp_rule(instance.user, 'DISCONNECT_SERVICE')

# RULE XP5 #


@receiver(post_save, sender=Idea)
def on_idea_created(sender, instance, created, **kwargs):
    if created:
        apply_xp_rule(instance.user, 'NEW_IDEA')

# RULE XP6 #


@receiver(post_save, sender=ProjectFollowing)
def on_project_following_created(sender, instance, created, **kwargs):
    if created:
        apply_xp_rule(instance.user, 'PROJECT_FOLLOW')

# RULE XP7 #


@receiver(platform_invitation_accepted, sender=PlatformInvitation)
def on_platform_invitation_accepted(sender, invitation, **kwargs):
    apply_xp_rule(invitation.user, 'INVITATION_ACCEPTED')

# TODO IMPLEMENT RULE XP8 #
# TODO IMPLEMENT RULE XP9 #

# RULE XP10 #


@receiver(visited_activity_tracker_home, sender=User)
def on_visit_activity_tracker_home(sender, user, **kwargs):
    apply_xp_rule(user, 'OPEN_ACTIVITY_TRACKER')
