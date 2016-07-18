from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect

from ct_projects.models import Notification
from profile.forms import UserProfileForm
from profile.lists import DEFAULT_BRANDS, BRAND_OPINIONS
from profile.models import UserBrandOpinion, UserProfile, Influence, DeviceUsage, PlatformUsage
from profile.templatetags.profile_tags import get_brand_icon


@login_required
def view_my_profile(request):
    # load profile
    profile = request.user.profile
    params = {
        'profile': profile,
        'liked_brands': [op.brand for op in profile.user.brand_opinions.filter(opinion='P')],
        'disliked_brands': [op.brand for op in profile.user.brand_opinions.filter(opinion='N')],
    }

    if profile.has_been_saved:  # proceed to details page
        return render(request, 'profile/index.html', params)
    else:
        return redirect(reverse('start-profile-wizard'))


@login_required
def start_wizard(request):
    # initialize profile form variables
    profile = request.user.profile
    params = {
        'profile': profile,
        'profile_edit': True,
    }

    if request.method == 'GET':
        form = UserProfileForm(instance=profile)
    else:
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # save the profile
            profile = form.save(commit=False)
            profile.has_been_saved = True
            profile.save()

            # add related information
            for influence in form.cleaned_data['influences']:
                if Influence.objects.filter(user=profile.user, influence=influence).count() == 0:
                    Influence.objects.create(user=profile.user, influence=influence)

            for influence in Influence.objects.filter(user=profile.user):
                if influence.influence not in form.cleaned_data['influences']:
                    influence.delete()

            for device in form.cleaned_data['devices']:
                if DeviceUsage.objects.filter(user=profile.user, device=device).count() == 0:
                    DeviceUsage.objects.create(user=profile.user, device=device)

            for device_usage in DeviceUsage.objects.filter(user=profile.user):
                if device_usage.device not in form.cleaned_data['devices']:
                    device_usage.delete()

            for platform in form.cleaned_data['platforms']:
                if PlatformUsage.objects.filter(user=profile.user, platform=platform).count() == 0:
                    PlatformUsage.objects.create(user=profile.user, platform=platform)

            for platform_usage in PlatformUsage.objects.filter(user=profile.user):
                if platform_usage.platform not in form.cleaned_data['platforms']:
                    platform_usage.delete()

            # update user
            profile.user.location = form.cleaned_data['location']
            profile.user.save()

            return redirect(reverse('start-profile-wizard'))

    params['form'] = form
    return render(request, 'profile/edit.html', params)


@login_required
def get_brand_opinion(request):
    # find the first brand that user has given no opinion about
    brand = None
    for b in DEFAULT_BRANDS:
        if not UserBrandOpinion.objects.filter(user=request.user, brand=b[0]):
            brand = b[0]
            break

    if not brand:
        return HttpResponse('')
    else:
        return render(request, 'profile/brand-opinion/form.html', {
            'brand': brand,
            'brand_icon': get_brand_icon(brand),
        })


def opinion_about(request):
    if request.method != 'POST':
        return HttpResponse('Only POST allowed', status=400)

    # get parameters
    brand = request.POST.get('brand', '')
    opinion = request.POST.get('opinion', '')

    # validation
    errors = []
    if brand not in [b[0] for b in DEFAULT_BRANDS]:
        errors.append('Brand must be one of %s' % ','.join([b[1] for b in DEFAULT_BRANDS]))

    if opinion not in [o[0] for o in BRAND_OPINIONS]:
        errors.append('Opinion must be one of %s' % ','.join([o[1] for o in BRAND_OPINIONS]))

    bo = UserBrandOpinion.objects.filter(user=request.user, brand=brand)
    if bo:
        bo = bo[0]
        bo.opinion = opinion
        bo.save()
    else:
        UserBrandOpinion.objects.create(user=request.user, brand=brand, opinion=opinion)

    return HttpResponse('')


@login_required
def notifications(request):
    ctx = {
        'notifications': [n for n in Notification.objects.filter(user=request.user)
                          if (not n.campaign()) or (not n.campaign().has_expired())]
    }

    return render(request, 'profile/notification/all.html', ctx)


@login_required
def notification_view(request, pk):
    try:
        notification = Notification.objects.get(pk=int(pk), user=request.user)
    except Notification.DoesNotExist:
        return redirect(reverse('notifications'))
    except ValueError:
        return redirect(reverse('notifications'))

    # mark notification as seen
    notification.seen = True
    notification.save()

    return redirect(notification.url(user=request.user))
