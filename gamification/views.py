from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from gamification.signals import *


@login_required
def leaderboard(request):
    ctx = {
        'leaderboard': request.user.gamification_profile.xp_leaderboard(),
    }

    return render(request, 'gamification/leaderboard-content.html', ctx)


@login_required
def badge_collection(request):
    # get all badges
    badge_list = Badge.objects.filter(active=True)[:]
    badge_rewards = BadgeReward.objects.filter(user_id=request.user.pk)

    # find on which of them user has been rewarded
    for br in badge_rewards:
        for b in badge_list:
            if br.badge_id == b.pk:
                b.rewarded = br
                break

    ctx = {
        'badges': badge_list,
        'badge_rewards': badge_rewards,
    }

    return render(request, 'gamification/badge-collection-content.html', ctx)
