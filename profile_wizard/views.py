from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from profile_wizard.forms import UserProfileForm


@login_required
def start_wizard(request):
    # initialize vars
    profile = request.user.profile
    params = {
        'profile': profile,
    }

    if request.method == 'GET':
        form = UserProfileForm(instance=profile)
    else:
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # save the profile
            form.save()

            # TODO parse & save add brand opinions
            return redirect('/')

    params['form'] = form
    return render(request, 'profile_wizard/start.html', params)
