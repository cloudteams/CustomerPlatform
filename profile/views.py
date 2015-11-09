from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.templatetags.static import static
from profile.forms import UserProfileForm
from profile.lists import DEFAULT_BRANDS, BRAND_OPINIONS
from profile.models import UserBrandOpinion, UserProfile


@login_required
def view_my_profile(request):
    # load profile
    profile = request.user.profile
    params = {
        'profile': profile,
        'influences_field': UserProfile.influences.field,
        'devices_field': UserProfile.devices.field,
        'platforms_field': UserProfile.platforms.field,
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

            # update user
            profile.user.location = form.cleaned_data['location']
            profile.user.save()

            return redirect(reverse('start-profile-wizard'))

    params['form'] = form
    return render(request, 'profile/edit.html', params)


def get_brand_icon(brand):
    return static('profile/img/brands/%s.png' % brand.lower())


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
