from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from gamification.signals import *


@login_required
def leaderboard(request):
    ctx = {
        'leaderboard': request.user.gamification_profile.xp_leaderboard(),
    }

    return render(request, 'gamification/leaderboard-content.html', ctx)
