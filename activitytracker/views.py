from django.dispatch import Signal
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate

from Activitytracker_Project.settings import DEFAULT_FROM_EMAIL
from activitytracker.models import *
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.template.response import SimpleTemplateResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage
from config import *
from operator import itemgetter
import string
import random
import json

import calendar
import operator
import collections
from myfunctions import *
from AuthorizationChecks import *
from config import *
from InstagramClass import Instagram
from TwitterClass import Twitter
from YoutubeClass import Youtube
from RunkeeperClass import Runkeeper
from FitbitClass import Fitbit
from FoursquareClass import Foursquare
from FacebookActivityClass import FacebookActivity
from datetime import datetime
from django.db.models import Q

from profile.models import PlatformInvitation, TeamInvitation

colourDict = {'black': "rgba(1, 1, 1, 0.8)",
              'blue': "#578EBE",
              'greenLight': "#99B433",
              'orange': "#e09100",
              'redDark': "#850521",
              'purple': "#800080"
              }

basic_routine_activities = [
    'Eating',
    'Working',
    'Commuting',
    'Education',
    'Sleeping'
]

day_types = [
    'Weekdays',
    'Weekend'
]


def terms_and_conditions(request):
    return render(request, 'activitytracker/terms_and_conditions.html', {})


def login(request):

    EMAIL_VERIFICATION_MSG = 'You need to verify your E-mail in order to log in'
    INVALID_CREDENTIALS_MSG = 'Invalid Username/Email or Password'

    redirect_url = request.GET.get('next', '/projects/')
    ctx = {
        'redirect_url': redirect_url,
        'ignore_login_link': True,
        'light_menu': True,
        'register_button': True,
    }

    if request.method != 'POST':
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('followed-projects'))

        return render(request, 'activitytracker/login.html', ctx)

    username_or_email = request.POST['username']
    password = request.POST['password']
    ctx['username'] = username_or_email

    if User.objects.filter(username__iexact=username_or_email).count() == 0:

        if User.objects.filter(email__iexact=username_or_email).count() == 0:
            ctx['error'] = INVALID_CREDENTIALS_MSG
            return render(request, 'activitytracker/login.html', ctx)
        else:
            username = User.objects.get(email__iexact=username_or_email).username

    else:
        username = username_or_email

    user = authenticate(username=username, password=password)

    if user is None:
        ctx['error'] = INVALID_CREDENTIALS_MSG
        return render(request, 'activitytracker/login.html', ctx)

    if not user.is_active:
        ctx['error'] = EMAIL_VERIFICATION_MSG
        return render(request, 'activitytracker/login.html', ctx)

    auth_login(request, user)

    return redirect(redirect_url)


# Flush Session and redirect
def logout(request):

    auth_logout(request)
    return HttpResponseRedirect(reverse('login'))


# Check and Register the User
def register(request):

    USERNAME_EXISTS_MSG = 'This username is already used'
    EMAIL_EXISTS_MSG = 'A user with this email address already exists'
    EMPTY_FIELDS_MSG = 'All fields are required'
    PASSWORD_ERROR = 'The passwords should match each other'

    if request.method != 'POST':
        ctx = {
            'ignore_login_link': True,
            'username': '',
            'email': '',
        }

        # auto-complete invitation registrations
        if 'ref_id' in request.GET:
            try:
                invitation = PlatformInvitation.objects.get(pk=int(request.GET.get('ref_id')))

                ctx['email'] = invitation.email
                ctx['username'] = invitation.email.split('@')[0]
            except PlatformInvitation.DoesNotExist:
                pass
            except ValueError:
                pass
        # auto-complete invitation registrations
        elif 'team_ref_id' in request.GET:
            try:
                invitation = TeamInvitation.objects.get(pk=int(request.GET.get('team_ref_id')))

                ctx['email'] = invitation.email
                ctx['username'] = invitation.email.split('@')[0]
            except PlatformInvitation.DoesNotExist:
                pass
            except ValueError:
                pass

        return render(request, 'activitytracker/register.html', ctx)

    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    repeated_password = request.POST['password_repeat']

    ctx = {
        'username': username,
        'email': email,
        'errors': []
    }

    if User.objects.filter(username__iexact=username).exists():
        ctx['errors'].append(USERNAME_EXISTS_MSG)

    if User.objects.filter(email__iexact=email).exists():
        ctx['errors'].append(EMAIL_EXISTS_MSG)

    if password != repeated_password:
        ctx['errors'].append(PASSWORD_ERROR)

    if '' in (email, password, repeated_password):
        ctx['errors'].append(EMPTY_FIELDS_MSG)

    if ctx['errors']:
        return render(request, 'activitytracker/register.html', ctx)

    username = email.split('@')[0] if not User.objects.filter(username=email.split('@')[0]).exists() else email

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )
    user.is_active = False
    user.save()

    characters = string.ascii_letters + string.digits
    verification_token = ''.join(random.choice(characters) for _ in range(20))
    verification_url = 'http://%s/activitytracker/account/verification/%s' % (request.get_host(), verification_token)
    verification_instance = UserUniqueTokens(
        user=user,
        token=verification_token,
        token_type="Verification"
    )
    verification_instance.save()

    email = DEFAULT_FROM_EMAIL
    mail_title = "CloudTeams account verification"
    recipient = [user.email.encode('utf8')]
    mail_message = 'Hello %s. In order to verify your account click the following link: %s' \
                   % (user.get_username(), verification_url)

    send_mail(mail_title, mail_message, email, recipient, fail_silently=False)

    return render(request, 'activitytracker/registration-success.html')


# Produce new random pass and send it with e-mail
def passwordforget(request):

    USER_NOT_EXISTS_MSG = 'No such User exists'
    NOT_VERIFIED_MSG = 'Please verify your account before you request a password recovery'
    SUCCESS_MSG = 'We have sent you an email with instructions on how to reset your password'


    if request.method != 'POST':
        return render(request, 'activitytracker/passforget.html')

    username_or_email = request.POST['username']

    if User.objects.filter(username__iexact=username_or_email).count() == 0:
        if User.objects.filter(email__iexact=username_or_email).count() == 0:
            return HttpResponseBadRequest(USER_NOT_EXISTS_MSG)
        else:
            username = User.objects.get(email__iexact=username_or_email).username

    else:
        username = username_or_email

    if not User.objects.get(username=username).is_active:
        return HttpResponseBadRequest(NOT_VERIFIED_MSG)

    user = User.objects.get(username=username)
    characters = string.ascii_letters + string.digits
    passwordforget_token = ''.join(random.choice(characters) for _ in range(20))
    passwordforget_url = '%s/activitytracker/account/password_reset/%s' % (request.get_host(), passwordforget_token)
    passwordforget_instance = UserUniqueTokens(
        user=user,
        token=passwordforget_token,
        token_type="PasswordReset"
    )
    passwordforget_instance.save()

    email = DEFAULT_FROM_EMAIL
    mail_title = "CloudTeams password reset"
    recipient = [user.email.encode('utf8')]
    mail_message = 'Hello %s. You have recently requested a password reset. Please follow this link in order to ' \
                   'start the process: %s' % (user.get_username(), passwordforget_url)

    send_mail(mail_title, mail_message, email, recipient, fail_silently=False)

    return HttpResponse(SUCCESS_MSG)

# If token is correct, it loads a proper page to reset the password
def password_reset(request, passwordreset_token):

    PASSWORD_MISMATCH_ERROR = "The password you entered don't match each other. Try again"
    SUCCESS_MSG = "Your password has been successfully updated"

    try:
        token_instance = UserUniqueTokens.objects.get(
            token=passwordreset_token,
            token_type="PasswordReset"
        )
        valid_token = True

    except ObjectDoesNotExist:
        valid_token = False

    if request.method != "POST" or not valid_token:
        return render(request,'activitytracker/password-reset.html',{
            'valid_token': valid_token,
            'token': passwordreset_token

        })

    else:
        password = request.POST['password']
        repeated_password = request.POST['repeated_password']
        if password != repeated_password:
            return HttpResponseBadRequest(PASSWORD_MISMATCH_ERROR)

        user = token_instance.user
        user.set_password(password)
        user.save()
        token_instance.delete()
        return HttpResponse(SUCCESS_MSG)

# Updates the password to its new value. Differs from the "change password" action, since it doesn't require an old pass
def forgotten_password_update(request):
    pass

# view to handle the email verification
def email_verification(request, verification_token):

    try:
        verification_instance = UserUniqueTokens.objects.get(
            token=verification_token,
            token_type="Verification"
        )
        user = verification_instance.user
        user.is_active = True
        user.save()
        verification_instance.delete()
        success = True

    except ObjectDoesNotExist:
        success = False

    return render(request,'activitytracker/account-verification.html',
                  {'verification_successful': success}
                  )



# Handle settings options
@login_required
def settings(request):

    WRONG_PASS_MSG = 'The password you entered didnt match your current password'
    EMPTY_FIELDS_MSG = 'You cannot have a field empty'
    USERNAME_EXISTS_MSG = 'This username is already in use'
    BIRTHDAY_ERROR_MSG = 'You cannot be born in the future, duh!'
    PASS_MISSMATCH_MSG = 'Sorry the passwords you entered didnt match eachother'

    user = request.user

    if request.method == 'POST':

        if request.POST['settingAction'] == 'deleteaccount':

            if user.check_password(request.POST['password']):
                user.delete()
                return HttpResponseRedirect(reverse('login'))

            return HttpResponseBadRequest(WRONG_PASS_MSG)

        elif request.POST['settingAction'] == 'editinfo':

                old_username = user.get_username()
                user.username = request.POST['username']
                user.first_name = request.POST['firstname']
                user.last_name = request.POST['lastname']
                user.gender = request.POST['gender']
                user.date_of_birth = datetime.strptime(request.POST['birthday'], "%m/%d/%Y").date()

                if '' in (user.username, user.first_name, user.last_name, user.gender):
                    return HttpResponseBadRequest(EMPTY_FIELDS_MSG)

                if user.username != old_username and User.objects.filter(username=user.username).count() > 0:
                    return HttpResponseBadRequest(USERNAME_EXISTS_MSG)

                if user.date_of_birth > datetime.now().date():
                    return HttpResponseBadRequest(BIRTHDAY_ERROR_MSG)

                user.save()

                return HttpResponse(json.dumps({
                                            'username': user.get_username(),
                                            'fname': user.first_name,
                                            'lname': user.last_name,
                                            'email': user.email,
                                            'birthday': request.POST['birthday'],
                                            'gender': user.gender,
                                            }
                                        ),
                                        content_type='application/json'
                                    )

        elif request.POST['settingAction'] == 'passchange':

            if request.POST['new_password'] != request.POST['new_password_repeat']:
                return HttpResponseBadRequest(PASS_MISSMATCH_MSG)

            if user.has_usable_password():
                if not user.check_password(request.POST['old_password']):
                    return HttpResponseBadRequest(WRONG_PASS_MSG)

            user.set_password(request.POST['new_password'])
            user.save()

            return HttpResponseRedirect(reverse('login'))

    gender = '' if not user.gender else user.gender
    birth = '' if not user.date_of_birth else user.date_of_birth.strftime("%m/%d/%Y")

    providerDomValues = {}

    for provider in AVAILABLE_PROVIDERS:

        if user.social_auth.filter(provider=provider).count() == 0:
            providerDomValues[provider] = getAppManagementDomValues("Not Connected", provider)
            continue

        provider_object = eval(provider.title().replace('-', ''))(user.social_auth.get(provider=provider))
        providerDomValues[provider] = getAppManagementDomValues(provider_object.validate(), provider)

    routine_activities = getFormattedRoutines(user, basic_routine_activities, day_types)
    routine_extra_activities = list()
    for activity in Activity.objects.all().order_by('activity_name'):
        if activity.activity_name not in basic_routine_activities:
            routine_extra_activities.append({
                'activity': activity.activity_name,
                'color': activity.category,
                'icon_classname': activity.icon_classname,
            })

    context = {'username': user.get_username(),
               'firstname': user.get_short_name(),
               'lastname': user.last_name,
               'email': user.email,
               'birth': birth,
               'gender': gender,
               'social_login': not user.has_usable_password(),
               'providerDomValues': providerDomValues,
               'routineActivities': routine_activities,
               'routineExtraActivities': routine_extra_activities
               }

    return render(request, 'activitytracker/settings.html', context)


# Handler for the Places in Settings.html
@login_required
def places(request):

    user = request.user

    if request.method != "POST":
        return HttpResponseRedirect(reverse('settings'))

    if request.POST['setting'] in ('addPlace', 'editPlace'):

        name = request.POST['place_name']
        address = request.POST['address']
        lat = request.POST['lat']
        lng = request.POST['lng']

        if not name:
            return HttpResponseBadRequest('Empty')

        if request.POST['setting'] == "addPlace":
            a = Places(user=user,
                       place_name=name,
                       place_address=address,
                       place_lat=lat,
                       place_lng=lng
                       )

        else:
            a = user.places_set.get(place_id=request.POST['place_id'])
            a.place_name, a.place_address = name, address
            a.place_lat, a.place_lng = lat, lng

        try:
            a.save()
            return HttpResponse('ok')

        except IntegrityError:
            return HttpResponseBadRequest('Unique')

    elif request.POST['setting'] == "deletePlace":

        place = user.places_set.get(place_id=request.POST['place_id'])
        place.delete()
        return HttpResponse('ok')


def placestojson(request):

    user = request.user
    json_list = {"data": []}

    for p in user.places_set.all():
        json_list['data'].append({
            'id': p.place_id,
            'lat': p.place_lat,
            'lng': p.place_lng,
            'place_name': p.place_name,
            'place_address': p.place_address
        })

    return HttpResponse(json.dumps(json_list), content_type='application/json')


visited_activity_tracker_home = Signal(providing_args=["user"])


# Basic View, Gets called on "History" page load
@login_required
def index(request, new_user=False):

    user = request.user

    new_user = True if new_user == "NewUser" else False

    activity_data = dict([(category, []) for ( _ , category) in Activity.CATEGORY_CHOICES])
    for activity in Activity.objects.all():
        activity_data[activity.get_category_display()].append(activity.activity_name)

    context = {
               'username': user.get_username(),
               'activity_data': activity_data,
               'show_carousel_guide': new_user
    }

    if not user.logged_in_before:

        context['show_carousel_guide'] = True
        user.logged_in_before = True
        user.save()

    # send signal that signifies the user visited the activity tracker
    visited_activity_tracker_home.send(sender=User, user=request.user)

    return render(request, 'activitytracker/index.html', context)


# Gets called on "Group common" click, to return grouped activities
def getgroupedactivities(request):

    user = request.user
    if len(request.POST['grouped_data']) == 0:
        return HttpResponse(json.dumps([]), content_type='application/json')

    ids = (request.POST['grouped_data']).split("_")
    instances = user.performs_set.filter(id__in=ids)
    json_list = list()

    if request.POST['box'] == "checked":

        entries = dict()

        for instance in instances:

            if instance.activity.activity_name in entries:
               entries[instance.activity.activity_name][0].end_date += instance.end_date - instance.start_date
               entries[instance.activity.activity_name][1] += '_%s' % str(instance.id)
               continue

            entries[instance.activity.activity_name] = [instance, str(instance.id)]

        for activity_name, activity_data in entries.iteritems():

            [instance, grouped_id] = activity_data

            json_list.append({
                'id': grouped_id,
                'start_date': instance.start_date.strftime('%Y%m%d%H%M'),
                'duration': instance.displayable_date(),
                'activity': instance.activity.activity_name,
                'colour': str(instance.activity.category),
                'icon_classname': instance.activity.icon_classname
            })

    else:
        for event in instances:
            json_list.append(
                            { 'id': event.id,
                               'start_date': event.start_date.strftime('%Y%m%d%H%M'),
                               'duration': event.displayable_date(),
                               'activity': event.activity.activity_name,
                               'colour': str(event.activity.category),
                               'icon_classname': event.activity.icon_classname
                            }
            )

    sort = request.POST['sort']

    if sort == "Activity":
        json_list = sorted(json_list, key=operator.itemgetter('activity', 'start_date'))
    elif sort == "Category":
        json_list = sorted(json_list, key=operator.itemgetter('colour', 'start_date'))
    else:
        json_list = sorted(json_list, key=operator.itemgetter('start_date'))

    return HttpResponse(json.dumps(json_list), content_type='application/json')


# Gets called each time an activity is added
def addactivity(request):

    DATE_FILL_ERROR = 'Please fill up date and time fields correctly'
    ACTIVITY_FILL_ERROR = 'You must select an activity'
    DATE_ERROR = 'Activity can\'t end sooner than it began'
    print request.POST
    if '' in (request.POST['start_date'],
              request.POST['end_date'],
              request.POST['start_time'],
              request.POST['end_time'],
              ):
        return HttpResponseBadRequest(DATE_FILL_ERROR)
    if not request.POST['name_of_activity']:
        return HttpResponseBadRequest(ACTIVITY_FILL_ERROR)

    user = request.user
    activity = Activity.objects.get(activity_name=request.POST['name_of_activity'])
    start_datetime = '%s %s:00' % (request.POST['start_date'], request.POST['start_time'])
    end_datetime = '%s %s:00' % (request.POST['end_date'], request.POST['end_time'])
    goal = request.POST['goal']
    goal_status = '' if 'goalstatus' not in request.POST else request.POST['goalstatus']
    result = request.POST['result']
    objects = request.POST['tool']
    friends = request.POST['friend_list']
    location_address = request.POST['location_address']
    location_lat = None if request.POST['lng'] == '' else request.POST['lat']
    location_lng = None if request.POST['lng'] == '' else request.POST['lng']

    start_datetime = datetime.strptime(start_datetime, "%m/%d/%Y %H:%M:%S")
    end_datetime = datetime.strptime(end_datetime, "%m/%d/%Y %H:%M:%S")

    if start_datetime > end_datetime:
        return HttpResponseBadRequest(DATE_ERROR)

    utc_offset = calculateUtcOffset(location_lat, location_lng, start_datetime)

    instance = addActivityFromProvider(user=user,
                                       activity=activity,
                                       start_date=start_datetime,
                                       end_date=end_datetime,
                                       goal=goal,
                                       goal_status=goal_status,
                                       friends=friends,
                                       objects=objects,
                                       result=result,
                                       location_lat=location_lat,
                                       location_lng=location_lng,
                                       location_address=location_address,
                                       utc_offset=utc_offset
                                       )

    return HttpResponse(
        json.dumps(
            {
                'id': str(instance.id),
                'duration': instance.displayable_date(),
                'activity': instance.activity.activity_name,
                'colour': instance.activity.category
            }
        ),
        content_type='application/json'
    )



# Gets called each time a single activity is clicked
def showactivity(request, performs_identification):

    user = request.user
    details = user.performs_set.get(id=performs_identification)
    tools = ', '.join(object.object_name for object in details.using.all())
    start_date = details.start_date.strftime('%m/%d/%Y')
    end_date = details.end_date.strftime('%m/%d/%Y')
    end_time = details.end_date.strftime('%H:%M')
    start_time = details.start_date.strftime('%H:%M')

    try:
        provider_instance = PerformsProviderInfo.objects.get(instance=details)
    except ObjectDoesNotExist:
        provider_instance = None

    context = {'instance': details,
               'tools': tools,
               'start_t': start_time,
               'end_t': end_time,
               'end_date': end_date,
               'start_date': start_date,
               'color': colourDict[details.activity.category],
               'performs_provider_instance': provider_instance
               }

    return SimpleTemplateResponse('activitytracker/display-activity.html', context)


# Gets called when a grouped activity needs to be shown
def showgroupactivity(request, group_identification):

    user = request.user
    id_list = group_identification.split('_')
    events = user.performs_set.filter(id__in=id_list).order_by('start_date')
    activity_group = []

    for details in events:
        tools_string = ', '.join(str(t.object_name) for t in details.using.all())
        start_date = details.start_date.strftime('%m/%d/%Y')
        end_date = details.end_date.strftime('%m/%d/%Y')
        start_time = details.start_date.strftime('%H:%M')
        end_time = details.end_date.strftime('%H:%M')
        colour = colourDict[details.activity.category]

        try:
            provider_instance = PerformsProviderInfo.objects.get(instance=details)
        except ObjectDoesNotExist:
            provider_instance = None

        activity_group.append({'tools': tools_string,
                             'start_time': start_time,
                             'end_time': end_time,
                             'end_date': end_date,
                             'start_date': start_date,
                             'instance': details,
                             'performs_provider_instance': provider_instance
                             })

    activities = {'activity_list': activity_group,
                  'color': colour,
                  'total_grouped_activities': len(id_list)
                  }

    return SimpleTemplateResponse('activitytracker/display-group-activity.html',
                                  activities
                                  )

# Deletes an activity
def deleteactivity(request, performs_id):

    activity = Performs.objects.get(id=performs_id)
    activity.delete()

    return HttpResponse('Deleted')


# Gives all the activities as JSON
@login_required
def listallactivities(request):

    context = {'activity_list': Activity.objects.all()}

    return render(request,
                  'activitytracker/activitytable.html',
                  context
                  )



#Gets called when Edit button is clicked, to instantiate values of inputs in the template
def editactivity(request, performs_id):

    user = request.user
    instance = Performs.objects.get(id=int(performs_id))
    start_date = instance.start_date.strftime('%m/%d/%Y')
    end_date = instance.end_date.strftime('%m/%d/%Y')
    end_time = instance.end_date.strftime('%H:%M')
    start_time = instance.start_date.strftime('%H:%M')
    instance_object_list = [i.object_name for i in instance.using.all()]
    instance_friend_list = filter(None, instance.friends.split(","))

    activity_data = dict([(category, []) for ( _ , category) in Activity.CATEGORY_CHOICES])
    for activity in Activity.objects.all():
        activity_data[activity.get_category_display()].append(activity.activity_name)

    context = {'instance': instance,
               'instance_object_list': json.dumps(instance_object_list),
               'instance_friend_list': json.dumps(instance_friend_list),
               'start_t': start_time,
               'end_t': end_time,
               'end_date': end_date,
               'start_date': start_date,
               'activity_data': activity_data,
               'color': colourDict[instance.activity.category],
               }

    return SimpleTemplateResponse('activitytracker/edit-activity.html', context)


def fetch_tokenfield_values(request):

    user = request.user
    object_values = [{'value': i.object_name, 'label': i.object_name} for i in user.object_set.all()] #for form
    friend_values = [{'value': i.friend_name, 'label': i.friend_name} for i in user.friend_set.all()] #for form

    json_list =[friend_values, object_values]
    return HttpResponse(json.dumps(json_list), content_type='application/json')




#Gets called on update activity
def updateactivity(request, performs_id):

    DATE_ERROR_MSG = 'Activity cannot end sooner than it started'
    FIELD_ERROR_MSG = 'Please fill out all the fields correctly'

    user = request.user
    instance = Performs.objects.get(id=performs_id)

    try:
        start_date = '%s %s:00' % (request.POST['start_date'], request.POST['start_time'])
        end_date = '%s %s:00' % (request.POST['end_date'], request.POST['end_time'])
        start_date = datetime.strptime(start_date, "%m/%d/%Y %H:%M:%S")
        end_date = datetime.strptime(end_date, "%m/%d/%Y %H:%M:%S")

        if start_date > end_date:
            return HttpResponseBadRequest(DATE_ERROR_MSG)

        activity = Activity.objects.get(activity_name=request.POST['name_of_activity'])
        friends = ','.join(list(set(request.POST['friend_list'].split(','))))
        objects = ','.join(list(set(request.POST['tool'].split(','))))
        location_address = request.POST['location_address']
        location_lat = request.POST['lat']
        location_lng = request.POST['lng']
        goal = request.POST['goal']
        result = request.POST['result']
        goal_status = None if not goal else request.POST['goalstatus']

        instance.delete()

        utc_offset = calculateUtcOffset(location_lat, location_lng, start_date)

        instance = addActivityFromProvider(user=user,
                                           activity=activity,
                                           start_date=start_date,
                                           end_date=end_date,
                                           goal=goal,
                                           goal_status=goal_status,
                                           friends=friends,
                                           objects=objects,
                                           result=result,
                                           location_lat=location_lat,
                                           location_lng=location_lng,
                                           location_address=location_address,
                                           utc_offset=utc_offset
                                           )

    except ValueError:
        return HttpResponseBadRequest({
            'code': 'DATE_ERROR_MSG',
            'msg': 'Activity cannot end sooner than it started'
        })

    return HttpResponse(
        json.dumps(
            {
                'id': str(instance.id),
                'duration': instance.displayable_date(),
                'activity': instance.activity.activity_name,
                'colour': instance.activity.category,
                'goal': instance.goal,
                'goal_status': instance.goal_status,
                'friends': instance.friends,
                'location_address': instance.location_address,
                'start_date': instance.start_date.strftime('%I:%M%p (%m/%d/%Y)'),
                'tools': ', '.join(t.object_name for t in instance.using.all()),
                'icon_classname': instance.activity.icon_classname,

            }
        ),
        content_type='application/json'
    )


# provides the JSON to the chart of Index Page
def chartdatajson(request):
    user = request.user

    if len(request.GET['chart_data']) == 0:
        return HttpResponse(json.dumps([]), content_type='application/json')

    ids = request.GET['chart_data'].split("_")
    instances = user.performs_set.filter(id__in=map(int, ids))

    chart_data = [
        {
            'label': category,
            'data': 0,
            'color': colourDict[colour]
        } for (colour, category) in Activity.CATEGORY_CHOICES
    ]

    for instance in instances:
        duration = instance.end_date - instance.start_date
        minutes = duration.seconds/60 + duration.days*24*60

        for index, category_dict in enumerate(chart_data):
            if category_dict['label'] == instance.activity.get_category_display():
                chart_data[index]['data'] += minutes
                break

    return HttpResponse(json.dumps(chart_data), content_type='application/json')

# Provides the event to the calendar
def eventstojson(request):

    user = request.user
    json_list = []

    for instance in user.performs_set.all():
        json_list.append({
            'id': instance.id,
            'start': instance.start_date.strftime("%Y-%m-%dT%H:%M:%S"),
            'allDay': False,
            'end': instance.end_date.strftime("%Y-%m-%dT%H:%M:%S"),
            'editable': False,
            'title': instance.activity.activity_name,
            'color': colourDict[instance.activity.category],
        })

    return HttpResponse(json.dumps(json_list), content_type='application/json')

# Gets called when calendar changes view
def displayperiod(request):

    user = request.user
    mode = request.POST['mode']

    if mode == "month":
        year = request.POST['year']
        month = request.POST['month']

        month_first_moment = datetime.strptime(
            '%s-%s-01 00:00:00' % (year, month),
            "%Y-%b-%d %H:%M:%S"
        )

        month_last_moment = datetime.strptime(
            '%s-%s-%s 23:59:59' % (year, month, str(calendar.monthrange(
                int(year),
                datetime.strptime(month, '%b').month)[1])
                                   ),
                "%Y-%b-%d %H:%M:%S"
        )

        instances = user.performs_set.filter(start_date__lte=month_last_moment,
                                             end_date__gte=month_first_moment
                                             )

    elif mode == "agendaDay":
        day = request.POST['day']
        year = request.POST['year']
        month = request.POST['month']

        day_first_moment = datetime.strptime('%s-%s-%s 00:00:00' % (year, month, day),
                                             "%Y-%B-%d %H:%M:%S"
                                             )

        day_last_moment = datetime.strptime('%s-%s-%s 23:59:59' % (year, month,day),
                                            "%Y-%B-%d %H:%M:%S"
                                            )

        instances = user.performs_set.filter(start_date__lte=day_last_moment,
                                             end_date__gte=day_first_moment
                                             )
    else:
        day = request.POST['day']
        year = request.POST['year']
        month = request.POST['month']

        day2 = request.POST['day2']
        year2 = request.POST['year2']
        month2 = request.POST['month2']

        week_first_moment = datetime.strptime('%s-%s-%s 00:00:00' % (year, month, day),
                                              "%Y-%b-%d %H:%M:%S"
                                              )

        week_last_moment = datetime.strptime('%s-%s-%s 23:59:59' % (year2, month2, day2),
                                             "%Y-%b-%d %H:%M:%S"
                                             )

        instances = user.performs_set.filter(start_date__lte=week_last_moment,
                                             end_date__gte=week_first_moment
                                             )

    ids = '_'.join(str(instance.id) for instance in instances)

    return HttpResponse(ids)


# Called to instantiate HTML and redirect to Goals Page
@login_required
def goals(request):

    user = request.user
    total_goals = len(user.performs_set.exclude(goal=""))

    return render(request,
                  'activitytracker/goals.html',
                  {
                      'username': user.get_username(),
                      'total_number': total_goals
                  }
                 )


# Feeds the jQuery.dataTable that is the table in the Goals page
def goalstojson(request):

    user = request.user
    json_list = {"data": []}
    activities = user.performs_set.exclude(goal="")

    for activity in activities:
        json_list['data'].append({
            'goal': activity.goal,
            'date': activity.start_date.strftime('%m/%d/%Y'),
            'activity': activity.activity.activity_name,
            'goal_status': activity.goal_status,
            'id': activity.id,
        })

    return HttpResponse(json.dumps(json_list), content_type='application/json')


# Gets called when any action from Goals.html is being performed
def goalhandler(request):

    DELETE_ERROR_MSG = 'Goal cant be empty! You can delete it though options'

    user = request.user
    setting = request.POST['setting']

    if setting == "deleteGoal":
        performs_instance = user.performs_set.get(id=request.POST['performs_id'])
        performs_instance.goal, performs_instance.goal_status = "", None
        performs_instance.save()
        return HttpResponse(len(user.performs_set.exclude(goal="")))

    elif setting == "updateGoal":
        updatedgoal = request.POST['data']
        updatedgoal_id = request.POST['performs_id']

        if updatedgoal == "":
            return HttpResponseBadRequest(DELETE_ERROR_MSG)

        performs_instance = user.performs_set.get(id=updatedgoal_id)
        performs_instance.goal = updatedgoal
        performs_instance.save()

        return HttpResponse('Ok')

    else:
        updategoalstatus_id = request.POST['performs_id']
        updategoalstatus_newstatus = request.POST['data']
        performs_instance = user.performs_set.get(id=updategoalstatus_id)
        performs_instance.goal_status = updategoalstatus_newstatus
        performs_instance.save()

        return HttpResponse('Ok')

# A json display of an activity that the user performs. Suitable for sync with other apps
def activitydetails(request, performs_id):

    user = request.user
    details = user.performs_set.get(id=performs_id)
    tools_string = ', '.join(t.object_name for t in details.using.all())

    json_list = {
        'id': details.id,
        'activity': details.activity.activity_name,
        'start_date': str(details.start_date),
        'end_date': str(details.end_date),
        'goal': details.goal,
        'goal_status': details.goal_status,
        'friends': details.friends,
        'tools': tools_string,
    }

    return HttpResponse(json.dumps(json_list), content_type='application/json')


# Loads the basic HTML of the Timeline Page
@login_required
def timeline(request):

    return render(
        request,
        'activitytracker/timeline.html',
        {
          'username': request.user.get_username()
        }
    )

 # Feeds the activities as json and paginates them to the html
def timeline_events_json(request):
    user = request.user

    total_events = user.performs_set.order_by('-start_date')
    paginator = Paginator(total_events, 10)
    requested_page = request.GET['page']
    json_list = []

    try:
        requested_events = paginator.page(requested_page)

        for instance in requested_events:
            tools_string = ', '.join(t.object_name for t in instance.using.all())
            start_date = instance.start_date.strftime('%I:%M%p (%m/%d/%Y)')
            json_entry = {
                'activity': instance.activity.activity_name,
                'start_date': start_date,
                'duration': instance.displayable_date(),
                'goal': instance.goal,
                'goal_status': instance.goal_status,
                'friends': instance.friends,
                'tools': tools_string,
                'result': instance.result,
                'colour': instance.activity.category,
                'id': instance.id,
                'location_address': instance.location_address,
                'icon_classname': instance.activity.icon_classname,
            }
            json_list.append(json_entry)

    except EmptyPage:
        pass

    return HttpResponse(json.dumps(json_list), content_type='application/json')

@login_required
def configuration(request):
    user = request.user

    routine_activities = getFormattedRoutines(user, basic_routine_activities, day_types)
    routine_extra_activities = list()
    for activity in Activity.objects.all().order_by('activity_name'):
        if activity.activity_name not in basic_routine_activities:
            routine_extra_activities.append({
                'activity': activity.activity_name,
                'color': activity.category,
                'icon_classname': activity.icon_classname,
            })

    return render(
        request,
        'activitytracker/configuration.html', {
            'username': user.get_username(),
            'routineActivities': routine_activities,
            'routineExtraActivities': routine_extra_activities
        }
    )

@login_required
def dashboard(request):

    user = request.user

    # Initialize the data. Cant do it in the same row, else they reference each other
    period_chart_data = collections.OrderedDict(
        [(d.strftime('%a'), {'count': 0, 'minutes': 0}) for d in (
            datetime.utcnow() + timedelta(days=counter) for counter in range(0, 7)
        )]
    )

    prev_period_chart_data = collections.OrderedDict(
        [(d.strftime('%a'), {'count':0, 'minutes': 0 }) for d in (
            datetime.utcnow() + timedelta(days=counter) for counter in range(0, 7)
        )]
    )

    day_order = [d.strftime('%a') for d in (
        datetime.utcnow() + timedelta(days=counter+1) for counter in range(0, 7)
    )]

    period_category_data = dict([
        (category, {
            'count': 0,
            'minutes': 0,
            'instance_percentage': 0,
            'time_percentage': 0,
            'color': color,
            'icon': icon
        })
        for ((color, category), (icon, _)) in zip(Activity.CATEGORY_CHOICES, Activity.CATEGORY_ICONS)])

    period_provider_data = dict([(provider, 0) for provider in AVAILABLE_PROVIDERS])

    lifetime_provider_data = dict([(provider, 0) for provider in AVAILABLE_PROVIDERS])

    period_top10_activity_data = dict()

    # Find the proper period ranges
    today = datetime.utcnow().date()

    end_of_period = datetime.now()
    start_of_period = datetime(today.year, today.month, today.day) - timedelta(days=6)
    end_of_prev_period = start_of_period - timedelta(seconds=1)
    start_of_prev_period = start_of_period - timedelta(days=7)

    # Total activities inside this week
    period_total_activities = user.performs_set.filter(
        start_date__lte=end_of_period,
        end_date__gte=start_of_period
    ).count()

    # Total unique activities inside this week
    period_total_different_activities = user.performs_set.filter(
        start_date__lte=end_of_period,
        end_date__gte=start_of_period
    ).values('activity__activity_name').distinct().count()

    # Initialize total duration and the activities-tracked counter
    period_total_minutes = 0
    period_tracked_activities = 0
    period_activities_with_friends = 0
    period_activities_with_location = 0

    # Find data of activities that occured in this week, 7 days before, up to today
    for user_instance in user.performs_set.filter(
            start_date__lte=end_of_period,
            end_date__gte=start_of_period
    ):
        # Group by Categories
        period_category_data[user_instance.activity.get_category_display()]['count'] += 1
        duration = round((user_instance.end_date - user_instance.start_date).seconds / float(60))
        period_category_data[user_instance.activity.get_category_display()]['minutes'] += duration

        period_chart_data[user_instance.start_date.strftime('%a')]['count'] += 1
        period_chart_data[user_instance.start_date.strftime('%a')]['minutes'] += duration

        # Group by Activities
        try:
            period_top10_activity_data[user_instance.activity.activity_name]['count'] += 1
            period_top10_activity_data[user_instance.activity.activity_name]['minutes'] += duration

        except KeyError:
            period_top10_activity_data[user_instance.activity.activity_name] = {'count': 1, 'minutes': duration}

        # Count period duration of Activities
        period_total_minutes += duration

        # Count and Bucket the Activities that derived from connected Services
        try:
            provider = PerformsProviderInfo.objects.get(instance=user_instance).provider.replace('_', '-')
            period_provider_data[provider] += 1
            period_tracked_activities += 1

        except ObjectDoesNotExist:
            pass

        # Count friends in activities of this period
        period_activities_with_friends += len(user_instance.friends.split(',')) if user_instance.friends else False

        # Count friends in activities of this period
        period_activities_with_location += 1 if user_instance.location_address else False

    # Find number and duration of activities that occured in the previous week
    for user_instance in user.performs_set.filter(
        start_date__lte=end_of_prev_period,
        end_date__gte=start_of_prev_period
    ):
        duration = round((user_instance.end_date - user_instance.start_date).seconds / float(60))
        prev_period_chart_data[user_instance.start_date.strftime('%a')]['count'] += 1
        prev_period_chart_data[user_instance.start_date.strftime('%a')]['minutes'] += duration

    # Calculate the percentages needed in the dashboard circle knobs
    for _, category_data in period_category_data.iteritems():
        try:
            category_data['instance_percentage'] = round(category_data['count']/float(period_total_activities), 3)*100
            category_data['time_percentage'] = round(category_data['minutes']/float(period_total_minutes), 3)*100
        except ZeroDivisionError:
            category_data['instance_percentage'] = category_data['time_percentage'] = 0

    # Find the Providers that the user has connected
    connected_providers = len(user.social_auth.filter(provider__in=AVAILABLE_PROVIDERS))
    total_providers = len(AVAILABLE_PROVIDERS)
    connected_provider_percentage = round(connected_providers/float(total_providers), 3)*100

    # Format the data to what the js charts expect
    category_chart_data = list()
    for (day, data), (_, prev_data) in zip(period_chart_data.items(), prev_period_chart_data.items()):
        category_chart_data.append({
            'day': day,
            'instances': data['count'],
            'minutes': data['minutes'],
            'type': (datetime.utcnow() - timedelta(days=6)).strftime('%b %d') + ' - Today',
            'period_order': 2
        })
        category_chart_data.append({
            'day': day,
            'instances': prev_data['count'],
            'minutes': prev_data['minutes'],
            'type': '%s - %s' % (
                (datetime.utcnow() - timedelta(days=13)).strftime('%b %d'),
                (datetime.utcnow() - timedelta(days=7)).strftime('%b %d')
            ),
            'period_order': 1
        })

    # And again format for the needed js charts
    provider_7day_activities_data = list([
        {'instances': instances, 'provider': provider} for provider, instances in period_provider_data.iteritems()
    ])

    provider_lifetime_activities_data = list([
        {'instances': instances, 'provider': provider} for provider, instances in lifetime_provider_data.iteritems()
    ])

    """
    ########################################################################################
        Top 10 and Latest 10 Activities of User in the Last 7 Days by Duration and Instances
    ########################################################################################
    """

    # Find the latest 10 activities entered
    latest_activity_list = list()
    for user_instance in user.performs_set.all().order_by('-start_date')[:10]:
        latest_activity_list.append({
            'id': user_instance.id,
            'name': user_instance.activity.activity_name,
            'icon': user_instance.activity.icon_classname,
            'start_time': user_instance.start_date.strftime('%m/%d/%Y %H:%M'),
            'duration': round((user_instance.end_date - user_instance.start_date).seconds / float(60))
        })

    # Format top 10 Activities for the JS Chart
    top_activities_chart_data = list()
    for activity, data in period_top10_activity_data.items():
        top_activities_chart_data.append({
            'name': activity,
            'instances': data['count'],
            'minutes': data['minutes']
        })

    # Get the Top 10 Activities by no. of instances
    top_activities_chart_data_by_instance = sorted(
        top_activities_chart_data,
        key=itemgetter('instances'),
        reverse=True
    )[:10]

    # Get the Top 10 Activities by duration
    top_activities_chart_data_by_duration = sorted(
        top_activities_chart_data,
        key=itemgetter('minutes'),
        reverse=True
    )[:10]


    """
    ##################################################
        Lifetime Data for the User
    ##################################################
    """

    # Lifetime Activities of User
    lifetime_activities = user.performs_set.all().count()

    # Lifetime Unique Activities of User
    lifetime_different_activities = user.performs_set.values('activity__activity_name').distinct().count()

    # Initialize other Lifetime Counters
    lifetime_minutes = 0
    lifetime_activities_with_friends = 0
    lifetime_activities_with_location = 0
    lifetime_tracked_activities = 0

    # For Lifetime Activities
    for instance in user.performs_set.all():

        # Count the number of Friends that participated
        lifetime_activities_with_friends += len(instance.friends.split(',')) if instance.friends else False

        # Count the number of locations the Activities took place
        lifetime_activities_with_location += 1 if instance.location_address else False

        # Count the total minutes
        lifetime_minutes += (instance.end_date - instance.start_date).seconds / 60

        # Count and bucket the activities that derived from Services and NOT manually inserted
        try:
            provider = PerformsProviderInfo.objects.get(instance=instance).provider.replace('_', '-')
            lifetime_provider_data[provider] += 1
            lifetime_tracked_activities += 1

        except ObjectDoesNotExist:
            pass

    provider_lifetime_activities_data = list([
        {'instances': instances, 'provider': provider} for provider, instances in lifetime_provider_data.iteritems()
    ])

    """
    #############################################
        End of Calculations
    #############################################
    """

    return render(request, 'activitytracker/dashboard.html', {
        'username': user.get_username(),
        'connected_providers': connected_providers,
        'connected_provider_percentage': connected_provider_percentage,
        'total_providers': total_providers,
        'period_category_data': period_category_data,
        'period_total_activities': period_total_activities,
        'period_total_different_activities': period_total_different_activities,
        'period_activities_with_location': period_activities_with_location,
        'period_activities_with_friends': period_activities_with_friends,
        'period_total_minutes': period_total_minutes,
        'chart_data': json.dumps(category_chart_data),
        'latest_activities': latest_activity_list,
        'top_activities_chart_data_by_instance': json.dumps(top_activities_chart_data_by_instance),
        'top_activities_chart_data_by_duration': json.dumps(top_activities_chart_data_by_duration),
        'period_tracked_activities': period_tracked_activities,
        'total_tracked_activities': lifetime_tracked_activities,
        'provider_7day_activities_data': json.dumps(provider_7day_activities_data),
        'provider_lifetime_activities_data': json.dumps(provider_lifetime_activities_data),
        'day_order': day_order,
        'total_activities': lifetime_activities,
        'total_different_activities': lifetime_different_activities,
        'total_minutes': lifetime_minutes,
        'total_activities_with_friends': lifetime_activities_with_friends,
        'total_activities_with_location': lifetime_activities_with_location
        }
    )

@login_required
def analytics_activities(request):
    user = request.user
    colourdict = {'black': 0, 'blue': 1, 'greenLight': 2,
                  'orange': 3, 'redDark': 4, 'purple': 5 }
    act_name_list = user.performs_set.values('activity__activity_name',
                                             'activity__category').order_by('activity__activity_name').distinct()
    activity_context_list = [[],[],[],[],[],[]]
    for activity in act_name_list:
        list_to_append = activity_context_list[colourdict[activity['activity__category']]]
        list_to_append.append(activity['activity__activity_name'])

    context_data = {
                    "Selfcare/Everyday Needs": activity_context_list[0],
                    "Communication/Socializing": activity_context_list[1],
                    "Sports/Fitness": activity_context_list[2],
                    "Fun/Leisure/Hobbies": activity_context_list[3],
                    "Responsibilities": activity_context_list[4],
                    "Transportation": activity_context_list[5],
                   }
    return render(request, 'activitytracker/analytics-activities.html',
                  {
                   'username': user.get_username(),
                   'activity_data': context_data,
                  }
    )


@login_required
def analytics_routine(request):

    user = request.user
    personal_routine_list = getRoutineList(user, basic_routine_activities)

    routine_activities = dict()
    for activity_name in personal_routine_list:

        activity = Activity.objects.get(activity_name=activity_name)
        routine_activities[activity.activity_name] = {
            'color': activity.category,
            'icon_classname': activity.icon_classname,
        }

    return render(request, 'activitytracker/analytics-routine.html',
                  {
                   'username': user.get_username(),
                   'routineActivities': routine_activities,
                  }
    )


@login_required
def analytics_friends(request):
    user = request.user
    colourdict = {'black': 0, 'blue': 1, 'greenLight': 2,
                  'orange': 3, 'redDark': 4, 'purple': 5 }
    act_name_list = user.performs_set.values('activity__activity_name',
                                             'activity__category').order_by('activity__activity_name').distinct()
    activity_context_list = [[],[],[],[],[],[]]
    for activity in act_name_list:
        list_to_append = activity_context_list[colourdict[activity['activity__category']]]
        list_to_append.append(activity['activity__activity_name'])

    context_data = {
                    "Selfcare/Everyday Needs": activity_context_list[0],
                    "Communication/Socializing": activity_context_list[1],
                    "Sports/Fitness": activity_context_list[2],
                    "Fun/Leisure/Hobbies": activity_context_list[3],
                    "Responsibilities": activity_context_list[4],
                    "Transportation": activity_context_list[5],
                   }
    friend_context_list = [i.friend_name for i in user.friend_set.all()]
    return render(request, 'activitytracker/analytics-friends.html',
                  {
                   'username': user.get_username(),
                   'activity_data': context_data,
                   'friend_data': friend_context_list
                  }
    )

@login_required
def analytics_places(request):
    user = request.user
    context_data = [p.place_name for p in user.places_set.all()]
    return render(request, 'activitytracker/analytics-places.html',
                 {
                   'username': user.get_username(),
                   'places_data': context_data,
                  }
    )

@login_required
def analytics_goals(request):
    user = request.user
    colourdict = {'black': 0, 'blue': 1, 'greenLight': 2,
                  'orange': 3, 'redDark': 4, 'purple': 5 }
    act_name_list = user.performs_set.values('activity__activity_name',
                                             'activity__category').order_by('activity__activity_name').distinct()
    activity_context_list = [[],[],[],[],[],[]]
    for activity in act_name_list:
        list_to_append = activity_context_list[colourdict[activity['activity__category']]]
        list_to_append.append(activity['activity__activity_name'])

    context_data = {
                    "Selfcare/Everyday Needs": activity_context_list[0],
                    "Communication/Socializing": activity_context_list[1],
                    "Sports/Fitness": activity_context_list[2],
                    "Fun/Leisure/Hobbies": activity_context_list[3],
                    "Responsibilities": activity_context_list[4],
                    "Transportation": activity_context_list[5],
                   }

    return render(request, 'activitytracker/analytics-goals.html',
                  {
                   'username': user.get_username(),
                   'activity_data': context_data,
                  }
    )

@login_required
def analytics_objects(request):
    user = request.user

    colourdict = {'black': 0, 'blue': 1, 'greenLight': 2,
                  'orange': 3, 'redDark': 4, 'purple': 5 }
    act_name_list = user.performs_set.values('activity__activity_name',
                                             'activity__category').order_by('activity__activity_name').distinct()
    activity_context_list = [[],[],[],[],[],[]]
    for activity in act_name_list:
        list_to_append = activity_context_list[colourdict[activity['activity__category']]]
        list_to_append.append(activity['activity__activity_name'])

    context_data = {
                    "Selfcare/Everyday Needs": activity_context_list[0],
                    "Communication/Socializing": activity_context_list[1],
                    "Sports/Fitness": activity_context_list[2],
                    "Fun/Leisure/Hobbies": activity_context_list[3],
                    "Responsibilities": activity_context_list[4],
                    "Transportation": activity_context_list[5],
                   }
    object_context_list = []
    objects = user.object_set.all()
    for object in objects:
        object_context_list.append(object.object_name)
    return render(request, 'activitytracker/analytics-objects.html',
                  {
                   'username': user.get_username(),
                   'activity_data': context_data,
                   'object_data': object_context_list
                  }
    )

def updateonefriendmanyactivitiescharts(request):
    colourDict = {'black': "rgba(1, 1, 1, 0.8)",
                  'blue': "#578EBE",
                  'greenLight': "#99B433",
                  'orange': "#e09100",
                  'redDark': "rgb(148, 5, 37)",
                  'purple': "#800080"
    }
    user = request.user
    friend_selected = request.POST['friend']
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment).order_by('activity__category')
    chart_outer_data = collections.OrderedDict()
    chart_inner_data = collections.OrderedDict()
    count = 1

    for activity_instance in instances:
        if friend_selected in activity_instance.friends:
            if ((friend_selected == "") and (activity_instance.friends == "")) or ((friend_selected != "") and (activity_instance.friends != "")):
                try:
                    chart_inner_data[activity_instance.activity.get_category_display()]['count'] += 1
                    chart_inner_data[activity_instance.activity.get_category_display()]['time'] += activity_instance.end_date - activity_instance.start_date
                except KeyError:
                    chart_inner_data[activity_instance.activity.get_category_display()] = {}
                    chart_inner_data[activity_instance.activity.get_category_display()]['count'] = 1
                    chart_inner_data[activity_instance.activity.get_category_display()]['time'] = activity_instance.end_date - activity_instance.start_date
                    chart_inner_data[activity_instance.activity.get_category_display()]['color'] = colourDict[activity_instance.activity.category]
                try:
                    chart_outer_data[activity_instance.activity.activity_name]['count'] += 1
                    chart_outer_data[activity_instance.activity.activity_name]['time'] += activity_instance.end_date - activity_instance.start_date
                except KeyError:
                    chart_outer_data[activity_instance.activity.activity_name] = {}
                    chart_outer_data[activity_instance.activity.activity_name]['count'] = 1
                    chart_outer_data[activity_instance.activity.activity_name]['time'] = activity_instance.end_date - activity_instance.start_date
    json_list = [[], []]
    for key, value in chart_inner_data.iteritems():
        json_entry = {'Category': key ,
                      'Hours': round(value['time'].seconds/float(3600) + value['time'].days*float(24), 2),
                      'Instances': str(value['count']),
                      'Color': value['color'],
                      }
        json_list[0].append(json_entry)

    for key, value in chart_outer_data.iteritems():
        json_entry = {'Activity': key ,
                      'Timeorder': count,
                      'Instances': str(value['count']),
                      'Hours': round(value['time'].seconds/float(3600) + value['time'].days*float(24), 2),
                      'Category': Activity.objects.get(activity_name=key).get_category_display()
                      }
        json_list[1].append(json_entry)
        count += 1

    return HttpResponse(json.dumps(json_list), content_type='application/json')


def updateoneactivitymanyfriendscharts(request):
    user = request.user
    activity_selected = request.POST['activity']
    activity_object = Activity.objects.get(activity_name=activity_selected)
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment, activity=activity_object)

    chart_data = collections.OrderedDict()
    friends = [i.friend_name for i in user.friend_set.all()]
    count = 1
    barChart_data = []
    for activity_instance in instances:
        duration = activity_instance.end_date - activity_instance.start_date
        if activity_instance.friends != "":
            for friend in friends:
                if friend in activity_instance.friends:
                    dummy_dict = {
                                'Timeorder': count,
                                'Start_Date': activity_instance.start_date.strftime("%m/%d/%Y %H:%M"),
                                'Hours': round(duration.seconds/float(3600) + duration.days*float(24), 2),
                                'Friend': friend
                                }
                    barChart_data.append(dummy_dict)
                    try:
                        chart_data[friend]['count'] += 1
                        chart_data[friend]['time'] += activity_instance.end_date - activity_instance.start_date
                    except KeyError:
                        chart_data[friend] = {}
                        chart_data[friend]['count'] = 1
                        chart_data[friend]['time'] = activity_instance.end_date - activity_instance.start_date

        else:
            dummy_dict = {
                        'Timeorder': count,
                        'Start_Date': activity_instance.start_date.strftime("%m/%d/%Y %H:%M"),
                        'Hours': round(duration.seconds/float(3600) + duration.days*float(24), 2),
                        'Friend': 'Alone'
            }
            barChart_data.append(dummy_dict)
            try:
                chart_data['Alone']['count'] += 1
                chart_data['Alone']['time'] += activity_instance.end_date - activity_instance.start_date
            except KeyError:
                chart_data['Alone'] = {}
                chart_data['Alone']['count'] = 1
                chart_data['Alone']['time'] = activity_instance.end_date - activity_instance.start_date
        count += 1

    json_list = [[]]
    count = 1
    for key, value in chart_data.iteritems():
        json_entry = {'Friend': key ,
                      'Timeorder': count,
                      'Hours': round(value['time'].seconds/float(3600) + value['time'].days*float(24), 2),
                      'Instances': str(value['count']),
                      }
        json_list[0].append(json_entry)
        count += 1


    json_list.append(barChart_data)
    return HttpResponse(json.dumps(json_list), content_type='application/json')


def updateoneactivityonefriendchart(request):
    user = request.user
    activity_selected = request.POST['activity']
    friend_selected = request.POST['friend']
    activity_object = Activity.objects.get(activity_name=activity_selected)
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment, activity=activity_object)
    instances = instances.order_by('start_date')

    lineChart_data = []
    count = 1
    for activity_instance in instances:
        if friend_selected in activity_instance.friends:
            if ((friend_selected == "") and (activity_instance.friends == "")) or ((friend_selected != "") and (activity_instance.friends != "")):
                duration = activity_instance.end_date - activity_instance.start_date
                if activity_instance.goal != "":
                    if activity_instance.goal_status == "Reached":
                        goal_status_to_int = 3
                    elif activity_instance.goal_status == "Failed":
                        goal_status_to_int = 1
                    else:
                        goal_status_to_int = 2
                else:
                    goal_status_to_int = 0

                lineChart_data.append({
                                       'Timeorder': count,
                                       'Start_Date': activity_instance.start_date.strftime("%m/%d/%Y %H:%M"),
                                       'Hours': round(duration.seconds/float(3600) + duration.days*float(24), 2),
                                       'Goal_Status': goal_status_to_int
                                      })
                count += 1

    return HttpResponse(json.dumps(lineChart_data), content_type='application/json')


def updatemanyactivitiesmanyfriendschart(request):
    user = request.user
    friends = [i.friend_name for i in user.friend_set.all()]
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment)

    chart_data = {}
    for activity_instance in instances:
        if activity_instance.friends != "":
            for friend in friends:
                if friend in activity_instance.friends:
                    try:
                        chart_data[activity_instance.activity.activity_name][friend]['count'] += 1
                        chart_data[activity_instance.activity.activity_name][friend]['time'] += activity_instance.end_date - activity_instance.start_date
                    except KeyError:
                        try:
                            chart_data[activity_instance.activity.activity_name]
                        except KeyError:
                            chart_data[activity_instance.activity.activity_name] = {}
                        chart_data[activity_instance.activity.activity_name][friend] = {}
                        chart_data[activity_instance.activity.activity_name][friend]['count'] = 1
                        chart_data[activity_instance.activity.activity_name][friend]['time'] = activity_instance.end_date - activity_instance.start_date

        else:

            try:
                chart_data[activity_instance.activity.activity_name]['Alone']['count'] += 1
                chart_data[activity_instance.activity.activity_name]['Alone']['time'] += activity_instance.end_date - activity_instance.start_date
            except KeyError:
                try:
                    chart_data[activity_instance.activity.activity_name]
                except KeyError:
                    chart_data[activity_instance.activity.activity_name] = {}
                chart_data[activity_instance.activity.activity_name]['Alone'] = {}
                chart_data[activity_instance.activity.activity_name]['Alone']['count'] = 1
                chart_data[activity_instance.activity.activity_name]['Alone']['time'] = activity_instance.end_date - activity_instance.start_date

    json_list = []
    for key, value in chart_data.iteritems():
        for inner_key, inner_value in value.iteritems():
            json_entry = {'Activity': key ,
                          'Friend': inner_key,
                          'Instances': str(inner_value['count']),
                          'Hours': round(inner_value['time'].seconds/float(3600) + inner_value['time'].days*float(24), 2),
                          }
            json_list.append(json_entry)

    return HttpResponse(json.dumps(json_list), content_type='application/json')

def updatefriendsbanner(request):
    user = request.user
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    friend_selected = request.POST['friend']
    total_time_spent_with_friends = datetime.now() - datetime.now()
    activity_selected = request.POST['activity']
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")

    if activity_selected == "all":
        instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment)
    else:
        activity_object = Activity.objects.get(activity_name=activity_selected)
        instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment, activity=activity_object)

    if friend_selected == 'all':
        total_activities_with_friends = len(instances.exclude(friends__exact=""))
        for activity_instance in instances.exclude(friends__exact=""):
            total_time_spent_with_friends += activity_instance.end_date - activity_instance.start_date
            dummy_datetime_object = activity_instance

    else:
        total_activities_with_friends = 0
        for activity_instance in instances:
            if ((friend_selected == "") and (activity_instance.friends == "")) or ((friend_selected != "") and (activity_instance.friends != "")):
                if friend_selected in activity_instance.friends:
                    total_time_spent_with_friends += activity_instance.end_date - activity_instance.start_date
                    total_activities_with_friends += 1
                    dummy_datetime_object = activity_instance

    try:
        dummy_datetime_object.start_date = datetime.now()
        dummy_datetime_object.end_date = datetime.now() + total_time_spent_with_friends
        printable_time = dummy_datetime_object.displayable_date()
    except UnboundLocalError:
        printable_time = "0d0h0m"

    total_activities = len(instances)
    try:
        percentage_of_activities_with_friends = round(total_activities_with_friends/float(total_activities), 3)*100
    except ZeroDivisionError:
        percentage_of_activities_with_friends = 0
    json_response = {
                    'total_activities': total_activities,
                    'total_activities_done_with_friends': total_activities_with_friends,
                    'percentage_of_activities_with_friends': percentage_of_activities_with_friends,
                    'total_time_spent_with_friends': printable_time
                    }
    return HttpResponse(json.dumps(json_response),content_type="application/json")


##################################################################################

def updateoneobjectmanyactivitiescharts(request):
    colourDict = {'black': "rgba(1, 1, 1, 0.8)",
                  'blue': "#578EBE",
                  'greenLight': "#99B433",
                  'orange': "#e09100",
                  'redDark': "rgb(148, 5, 37)",
                  'purple': "#800080"
    }
    user = request.user
    object_selected = request.POST['object']
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment).order_by('activity__category')
    chart_outer_data = collections.OrderedDict()
    chart_inner_data = collections.OrderedDict()
    count = 1
    for activity_instance in instances:
        objects_string = ', '.join(str(t.object_name) for t in activity_instance.using.all())
        if object_selected in objects_string:
            if ((object_selected == "") and (objects_string == "")) or ((object_selected != "") and (objects_string != "")):
                try:
                    chart_inner_data[activity_instance.activity.get_category_display()]['count'] += 1
                    chart_inner_data[activity_instance.activity.get_category_display()]['time'] += activity_instance.end_date - activity_instance.start_date
                except KeyError:
                    chart_inner_data[activity_instance.activity.get_category_display()] = {}
                    chart_inner_data[activity_instance.activity.get_category_display()]['count'] = 1
                    chart_inner_data[activity_instance.activity.get_category_display()]['time'] = activity_instance.end_date - activity_instance.start_date
                    chart_inner_data[activity_instance.activity.get_category_display()]['color'] = colourDict[activity_instance.activity.category]
                try:
                    chart_outer_data[activity_instance.activity.activity_name]['count'] += 1
                    chart_outer_data[activity_instance.activity.activity_name]['time'] += activity_instance.end_date - activity_instance.start_date
                except KeyError:
                    chart_outer_data[activity_instance.activity.activity_name] = {}
                    chart_outer_data[activity_instance.activity.activity_name]['count'] = 1
                    chart_outer_data[activity_instance.activity.activity_name]['time'] = activity_instance.end_date - activity_instance.start_date
    json_list = [[], []]
    for key, value in chart_inner_data.iteritems():
        json_entry = {'Category': key ,
                      'Hours': round(value['time'].seconds/float(3600) + value['time'].days*float(24), 2),
                      'Instances': str(value['count']),
                      'Color': value['color'],
                      }
        json_list[0].append(json_entry)

    for key, value in chart_outer_data.iteritems():
        json_entry = {'Activity': key ,
                      'Timeorder': count,
                      'Instances': str(value['count']),
                      'Hours': round(value['time'].seconds/float(3600) + value['time'].days*float(24), 2),
                      'Category': Activity.objects.get(activity_name=key).get_category_display()
                      }
        json_list[1].append(json_entry)
        count += 1

    return HttpResponse(json.dumps(json_list), content_type='application/json')


def updateoneactivitymanyobjectscharts(request):
    user = request.user
    activity_selected = request.POST['activity']
    activity_object = Activity.objects.get(activity_name=activity_selected)
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment, activity=activity_object)

    chart_data = collections.OrderedDict()
    all_objects = list(o.object_name for o in user.object_set.all())
    count = 1
    barChart_data = []
    for activity_instance in instances:
        duration = activity_instance.end_date - activity_instance.start_date
        activity_objects_string = ', '.join(str(t.object_name) for t in activity_instance.using.all())
        if activity_objects_string != "":
            for obj in all_objects:
                if obj in activity_objects_string:
                    dummy_dict = {
                                'Timeorder': count,
                                'Start_Date': activity_instance.start_date.strftime("%m/%d/%Y %H:%M"),
                                'Hours': round(duration.seconds/float(3600) + duration.days*float(24), 2),
                                'Object': obj
                                }
                    barChart_data.append(dummy_dict)
                    try:
                        chart_data[obj]['count'] += 1
                        chart_data[obj]['time'] += activity_instance.end_date - activity_instance.start_date
                    except KeyError:
                        chart_data[obj] = {}
                        chart_data[obj]['count'] = 1
                        chart_data[obj]['time'] = activity_instance.end_date - activity_instance.start_date

        else:
            dummy_dict = {
                        'Timeorder': count,
                        'Start_Date': activity_instance.start_date.strftime("%m/%d/%Y %H:%M"),
                        'Hours': round(duration.seconds/float(3600) + duration.days*float(24), 2),
                        'Object': 'No Object used'
            }
            barChart_data.append(dummy_dict)
            try:
                chart_data['No Object used']['count'] += 1
                chart_data['No Object used']['time'] += activity_instance.end_date - activity_instance.start_date
            except KeyError:
                chart_data['No Object used'] = {}
                chart_data['No Object used']['count'] = 1
                chart_data['No Object used']['time'] = activity_instance.end_date - activity_instance.start_date
        count += 1

    json_list = [[]]
    count = 1
    for key, value in chart_data.iteritems():
        json_entry = {'Object': key ,
                      'Timeorder': count,
                      'Hours': round(value['time'].seconds/float(3600) + value['time'].days*float(24), 2),
                      'Instances': str(value['count']),
                      }
        json_list[0].append(json_entry)
        count += 1


    json_list.append(barChart_data)
    return HttpResponse(json.dumps(json_list), content_type='application/json')


def updateoneactivityoneobjectchart(request):
    user = request.user
    activity_selected = request.POST['activity']
    object_selected = request.POST['object']
    activity_object = Activity.objects.get(activity_name=activity_selected)
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment, activity=activity_object)
    instances = instances.order_by('start_date')

    lineChart_data = []
    count = 1
    for activity_instance in instances:
        activity_objects_string = ', '.join(str(t.object_name) for t in activity_instance.using.all())
        if object_selected in activity_objects_string:
            if ((object_selected == "") and (activity_objects_string == "")) or ((object_selected != "") and (activity_objects_string != "")):
                duration = activity_instance.end_date - activity_instance.start_date
                if activity_instance.goal != "":
                    if activity_instance.goal_status == "Reached":
                        goal_status_to_int = 3
                    elif activity_instance.goal_status == "Failed":
                        goal_status_to_int = 1
                    else:
                        goal_status_to_int = 2
                else:
                    goal_status_to_int = 0

                lineChart_data.append({
                                       'Timeorder': count,
                                       'Start_Date': activity_instance.start_date.strftime("%m/%d/%Y %H:%M"),
                                       'Hours': round(duration.seconds/float(3600) + duration.days*float(24), 2),
                                       'Goal_Status': goal_status_to_int
                                      })
                count += 1

    return HttpResponse(json.dumps(lineChart_data), content_type='application/json')


def updatemanyactivitiesmanyobjectschart(request):
    user = request.user
    all_objects = list(o.object_name for o in user.object_set.all())
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment)

    chart_data = {}
    for activity_instance in instances:
        activity_objects_string = ', '.join(str(t.object_name) for t in activity_instance.using.all())
        if activity_objects_string != "":
            for obj in all_objects:
                if obj in activity_objects_string:
                    try:
                        chart_data[activity_instance.activity.activity_name][obj]['count'] += 1
                        chart_data[activity_instance.activity.activity_name][obj]['time'] += activity_instance.end_date - activity_instance.start_date
                    except KeyError:
                        try:
                            chart_data[activity_instance.activity.activity_name]
                        except KeyError:
                            chart_data[activity_instance.activity.activity_name] = {}
                        chart_data[activity_instance.activity.activity_name][obj] = {}
                        chart_data[activity_instance.activity.activity_name][obj]['count'] = 1
                        chart_data[activity_instance.activity.activity_name][obj]['time'] = activity_instance.end_date - activity_instance.start_date

        else:

            try:
                chart_data[activity_instance.activity.activity_name]['No Objects used']['count'] += 1
                chart_data[activity_instance.activity.activity_name]['No Objects used']['time'] += activity_instance.end_date - activity_instance.start_date
            except KeyError:
                try:
                    chart_data[activity_instance.activity.activity_name]
                except KeyError:
                    chart_data[activity_instance.activity.activity_name] = {}
                chart_data[activity_instance.activity.activity_name]['No Objects used'] = {}
                chart_data[activity_instance.activity.activity_name]['No Objects used']['count'] = 1
                chart_data[activity_instance.activity.activity_name]['No Objects used']['time'] = activity_instance.end_date - activity_instance.start_date

    json_list = []
    for key, value in chart_data.iteritems():
        for inner_key, inner_value in value.iteritems():
            json_entry = {'Activity': key ,
                          'Object': inner_key,
                          'Instances': str(inner_value['count']),
                          'Hours': round(inner_value['time'].seconds/float(3600) + inner_value['time'].days*float(24), 2),
                          }
            json_list.append(json_entry)

    return HttpResponse(json.dumps(json_list), content_type='application/json')

def updateobjectsbanner(request):
    user = request.user
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    object_selected = request.POST['object']
    total_time_with_objects = datetime.now() - datetime.now()
    activity_selected = request.POST['activity']
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")

    if activity_selected == "all":
        instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment)
    else:
        activity_object = Activity.objects.get(activity_name=activity_selected)
        instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment, activity=activity_object)

    if object_selected == 'all':
        total_activities_with_objects = len(instances.exclude(using=None))
        for activity_instance in instances.exclude(using=None):
            total_time_with_objects += activity_instance.end_date - activity_instance.start_date
            dummy_datetime_object = activity_instance

    else:
        total_activities_with_objects = 0
        for activity_instance in instances:
            activity_objects_string = ', '.join(str(t.object_name) for t in activity_instance.using.all())
            if ((object_selected == "") and (activity_objects_string == "")) or ((object_selected != "") and (activity_objects_string != "")):
                if object_selected in activity_objects_string:
                    total_time_with_objects += activity_instance.end_date - activity_instance.start_date
                    total_activities_with_objects += 1
                    dummy_datetime_object = activity_instance

    try:
        dummy_datetime_object.start_date = datetime.now()
        dummy_datetime_object.end_date = datetime.now() + total_time_with_objects
        printable_time = dummy_datetime_object.displayable_date()
    except UnboundLocalError:
        printable_time = "0d0h0m"

    total_activities = len(instances)
    try:
        percentage_of_activities_with_objects = round(total_activities_with_objects/float(total_activities), 3)*100
    except ZeroDivisionError:
        percentage_of_activities_with_objects = 0
    json_response = {
                    'total_activities': total_activities,
                    'total_activities_done_with_objects': total_activities_with_objects,
                    'percentage_of_activities_with_objects': percentage_of_activities_with_objects,
                    'total_time_with_objects': printable_time
                    }
    return HttpResponse(json.dumps(json_response),content_type="application/json")

def updateactivitydonutchart(request):
    user = request.user
    activity_selected = request.POST['activity']
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    if activity_selected != "all":
        activity_object = Activity.objects.get(activity_name=activity_selected)
        instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment, activity=activity_object)
    else:
        instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment)

    chart_data = {}
    for activity_instance in instances:
        if activity_instance.goal != "":
            if activity_instance.goal_status == "InProgress":
                activity_instance.goal_status = "In Progress"
            try:
                chart_data[activity_instance.goal_status] += 1
            except KeyError:
                chart_data[activity_instance.goal_status] = 1
        else:
            try:
                chart_data["No Goal set"] += 1
            except KeyError:
                chart_data["No Goal set"] = 1

    json_list = []
    for key, value in chart_data.iteritems():
        json_entry = {'Goal Status': key,
                      'Instances': value,
                      }
        json_list.append(json_entry)
    return HttpResponse(json.dumps(json_list), content_type='application/json')


def updateactivityandcategorybarchart(request):
    user = request.user
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment)

    chart_data_activities = {}
    chart_data_categories = {}
    for activity_instance in instances:
        if activity_instance.goal != "":
            if activity_instance.goal_status == "InProgress":
                activity_instance.goal_status = "In Progress"
            try:
                chart_data_categories[activity_instance.activity.get_category_display()][activity_instance.goal_status] += 1
            except KeyError:
                try:
                    chart_data_categories[activity_instance.activity.get_category_display()]
                except KeyError:
                    chart_data_categories[activity_instance.activity.get_category_display()] = {}
                chart_data_categories[activity_instance.activity.get_category_display()][activity_instance.goal_status] = 1
            try:
                chart_data_activities[activity_instance.activity.activity_name][activity_instance.goal_status] += 1
            except KeyError:
                try:
                    chart_data_activities[activity_instance.activity.activity_name]
                except KeyError:
                    chart_data_activities[activity_instance.activity.activity_name] = {}
                chart_data_activities[activity_instance.activity.activity_name][activity_instance.goal_status] = 1
        else:
            try:
                chart_data_categories[activity_instance.activity.get_category_display()]["No Goal set"] += 1
            except KeyError:
                try:
                    chart_data_categories[activity_instance.activity.get_category_display()]
                except KeyError:
                    chart_data_categories[activity_instance.activity.get_category_display()] = {}
                chart_data_categories[activity_instance.activity.get_category_display()]["No Goal set"] = 1

            try:
                chart_data_activities[activity_instance.activity.activity_name]["No Goal set"] += 1
            except KeyError:
                try:
                    chart_data_activities[activity_instance.activity.activity_name]
                except KeyError:
                    chart_data_activities[activity_instance.activity.activity_name] = {}
                chart_data_activities[activity_instance.activity.activity_name]["No Goal set"] = 1

    json_list = [[], []]
    for key, value in chart_data_activities.iteritems():
        for inner_key, inner_value in value.iteritems():
            json_entry = {'Activity': key,
                          'Goal Status': inner_key,
                          'Instances': inner_value,
                          }
            json_list[0].append(json_entry)

    for key, value in chart_data_categories.iteritems():
        for inner_key, inner_value in value.iteritems():
            json_entry = {'Category': key,
                          'Goal Status': inner_key,
                          'Instances': inner_value,
                          }
            json_list[1].append(json_entry)

    return HttpResponse(json.dumps(json_list), content_type='application/json')


def updateactivityandobjectbubblechart(request):
    user = request.user
    all_objects = list(o.object_name for o in user.object_set.all())
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment)

    chart_data = {}
    for activity_instance in instances:
        activity_objects_string = ', '.join(str(t.object_name) for t in activity_instance.using.all())
        if activity_instance.goal_status == "InProgress":
                activity_instance.goal_status = "In Progress"
        if activity_objects_string != "":
            for obj in all_objects:
                if obj in activity_objects_string:
                    if activity_instance.goal != "":
                        try:
                            chart_data[activity_instance.activity.activity_name][obj][activity_instance.goal_status] += 1
                        except KeyError:
                            try:
                                chart_data[activity_instance.activity.activity_name]
                            except KeyError:
                                chart_data[activity_instance.activity.activity_name] = {}
                            try:
                                chart_data[activity_instance.activity.activity_name][obj]
                            except KeyError:
                                chart_data[activity_instance.activity.activity_name][obj] = {}
                            chart_data[activity_instance.activity.activity_name][obj][activity_instance.goal_status] = 1
                    else:
                        try:
                            chart_data[activity_instance.activity.activity_name][obj]["No Goal set"] += 1
                        except KeyError:
                            try:
                                chart_data[activity_instance.activity.activity_name]
                            except KeyError:
                                chart_data[activity_instance.activity.activity_name] = {}
                            try:
                                chart_data[activity_instance.activity.activity_name][obj]
                            except KeyError:
                                chart_data[activity_instance.activity.activity_name][obj] = {}
                            chart_data[activity_instance.activity.activity_name][obj]["No Goal set"] = 1
        else:
            if activity_instance.goal != "":
                try:
                    chart_data[activity_instance.activity.activity_name]['No Objects used'][activity_instance.goal_status] += 1
                except KeyError:
                    try:
                        chart_data[activity_instance.activity.activity_name]
                    except KeyError:
                        chart_data[activity_instance.activity.activity_name] = {}
                    try:
                        chart_data[activity_instance.activity.activity_name]["No Objects used"]
                    except KeyError:
                        chart_data[activity_instance.activity.activity_name]["No Objects used"] = {}
                    chart_data[activity_instance.activity.activity_name]["No Objects used"][activity_instance.goal_status] = 1
            else:
                try:
                    chart_data[activity_instance.activity.activity_name]["No Objects used"]["No Goal set"] += 1
                except KeyError:
                    try:
                        chart_data[activity_instance.activity.activity_name]
                    except KeyError:
                        chart_data[activity_instance.activity.activity_name] = {}
                    try:
                        chart_data[activity_instance.activity.activity_name]["No Objects used"]
                    except KeyError:
                        chart_data[activity_instance.activity.activity_name]["No Objects used"] = {}
                    chart_data[activity_instance.activity.activity_name]["No Objects used"]["No Goal set"] = 1
    json_list = []
    for key, value in chart_data.iteritems():
        for inner_key, inner_value in value.iteritems():
            for status, status_instances in inner_value.iteritems():
                json_entry = {'Activity': key ,
                              'Object': inner_key,
                              'Goal Status': status,
                              'Instances': status_instances
                              }
                json_list.append(json_entry)
    return HttpResponse(json.dumps(json_list), content_type='application/json')


def updateactivitysandfriendbubblechart(request):
    user = request.user
    all_friends = [i.friend_name for i in user.friend_set.all()]
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment)

    chart_data = {}
    for activity_instance in instances:
        if activity_instance.friends != "":
            for friend in all_friends:
                if friend in activity_instance.friends:
                    if activity_instance.goal != "":
                        if activity_instance.goal_status == "InProgress":
                            activity_instance.goal_status = "In Progress"
                        try:
                            chart_data[activity_instance.activity.activity_name][friend][activity_instance.goal_status] += 1
                        except KeyError:
                            try:
                                chart_data[activity_instance.activity.activity_name]
                            except KeyError:
                                chart_data[activity_instance.activity.activity_name] = {}
                            try:
                                chart_data[activity_instance.activity.activity_name][friend]
                            except KeyError:
                                chart_data[activity_instance.activity.activity_name][friend] = {}
                            chart_data[activity_instance.activity.activity_name][friend][activity_instance.goal_status] = 1
                    else:
                        try:
                            chart_data[activity_instance.activity.activity_name][friend]["No Goal set"] += 1
                        except KeyError:
                            try:
                                chart_data[activity_instance.activity.activity_name]
                            except KeyError:
                                chart_data[activity_instance.activity.activity_name] = {}
                            try:
                                chart_data[activity_instance.activity.activity_name][friend]
                            except KeyError:
                                chart_data[activity_instance.activity.activity_name][friend] = {}
                            chart_data[activity_instance.activity.activity_name][friend]["No Goal set"] = 1
        else:
            if activity_instance.goal != "":
                try:
                    chart_data[activity_instance.activity.activity_name]['Alone'][activity_instance.goal_status] += 1
                except KeyError:
                    try:
                        chart_data[activity_instance.activity.activity_name]
                    except KeyError:
                        chart_data[activity_instance.activity.activity_name] = {}
                    try:
                        chart_data[activity_instance.activity.activity_name]["Alone"]
                    except KeyError:
                        chart_data[activity_instance.activity.activity_name]["Alone"] = {}
                    chart_data[activity_instance.activity.activity_name]["Alone"][activity_instance.goal_status] = 1
            else:
                try:
                    chart_data[activity_instance.activity.activity_name]["Alone"]["No Goal set"] += 1
                except KeyError:
                    try:
                        chart_data[activity_instance.activity.activity_name]
                    except KeyError:
                        chart_data[activity_instance.activity.activity_name] = {}
                    try:
                        chart_data[activity_instance.activity.activity_name]["Alone"]
                    except KeyError:
                        chart_data[activity_instance.activity.activity_name]["Alone"] = {}
                    chart_data[activity_instance.activity.activity_name]["Alone"]["No Goal set"] = 1
    json_list = []
    for key, value in chart_data.iteritems():
        for inner_key, inner_value in value.iteritems():
            for status, status_instances in inner_value.iteritems():
                json_entry = {'Activity': key ,
                              'Friend': inner_key,
                              'Goal Status': status,
                              'Instances': status_instances
                              }
                json_list.append(json_entry)
    return HttpResponse(json.dumps(json_list), content_type='application/json')

def updategoalsbanner(request):
    user = request.user
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    analysis_selected = request.POST['analysis']
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment)
    total_activities = len(instances)
    goals_reached = 0
    if analysis_selected == 'Activities & Categories':
        total_goals_set = len(instances.exclude(goal__exact=""))
        for activity_instance in instances.exclude(goal__exact=""):
            if activity_instance.goal_status == "Reached":
                goals_reached += 1
    elif analysis_selected == "Activity/Object":
        total_goals_set = len(instances.exclude(goal__exact="").exclude(using=None))
        for activity_instance in instances.exclude(goal__exact="").exclude(using=None):
            if activity_instance.goal_status == "Reached":
                goals_reached += 1
    else:
        total_goals_set = len(instances.exclude(goal__exact="").exclude(friends__exact=""))
        for activity_instance in instances.exclude(goal__exact="").exclude(friends__exact=""):
            if activity_instance.goal_status == "Reached":
                goals_reached += 1

    try:
        percentage_of_goals_reached = round(goals_reached/float(total_goals_set), 3)*100
    except ZeroDivisionError:
        percentage_of_goals_reached = 0
    json_response = {
                    'total_activities': total_activities,
                    'total_goals_set': total_goals_set,
                    'percentage_of_goals_reached': percentage_of_goals_reached,
                    }
    return HttpResponse(json.dumps(json_response),content_type="application/json")


def updateactivitiesinplacedonutchart(request):
    colourDict = {'black': "rgba(1, 1, 1, 0.8)",
                  'blue': "#578EBE",
                  'greenLight': "#99B433",
                  'orange': "#e09100",
                  'redDark': "rgb(148, 5, 37)",
                  'purple': "#800080"
    }

    pinColourDict = {'black': "black",
                     'blue': "blue",
                     'greenLight': "green",
                     'orange': "orange",
                     'redDark': "red",
                     'purple': "purple"
    }
    user = request.user
    radius_selected = request.POST['radius']
    place_selected = request.POST['place']

    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment).order_by('activity__category')
    chart_outer_data = collections.OrderedDict()
    chart_inner_data = collections.OrderedDict()
    json_list = [[], [], [], []]
    count = 1

    for activity_instance in instances:
        if activity_instance.location_address != "":
            if placesNearActivity(user, activity_instance, place_selected, radius_selected) != [] or place_selected == "all":
                json_list[2].append({'activity': activity_instance.activity.activity_name,
                                     'start_date': activity_instance.start_date.strftime("%m/%d/%Y %H:%M"),
                                     'duration': activity_instance.displayable_date(),
                                     'pinColor': pinColourDict[activity_instance.activity.category],
                                     'lat':activity_instance.location_lat,
                                     'lng':activity_instance.location_lng
                })


                try:
                    chart_inner_data[activity_instance.activity.get_category_display()]['count'] += 1
                    chart_inner_data[activity_instance.activity.get_category_display()]['time'] += activity_instance.end_date - activity_instance.start_date
                except KeyError:
                    chart_inner_data[activity_instance.activity.get_category_display()] = {}
                    chart_inner_data[activity_instance.activity.get_category_display()]['count'] = 1
                    chart_inner_data[activity_instance.activity.get_category_display()]['time'] = activity_instance.end_date - activity_instance.start_date
                    chart_inner_data[activity_instance.activity.get_category_display()]['color'] = colourDict[activity_instance.activity.category]
                try:
                    chart_outer_data[activity_instance.activity.activity_name]['count'] += 1
                    chart_outer_data[activity_instance.activity.activity_name]['time'] += activity_instance.end_date - activity_instance.start_date
                except KeyError:
                    chart_outer_data[activity_instance.activity.activity_name] = {}
                    chart_outer_data[activity_instance.activity.activity_name]['count'] = 1
                    chart_outer_data[activity_instance.activity.activity_name]['time'] = activity_instance.end_date - activity_instance.start_date

    # Return the data necessary for the inner ring of the double-donut chart (categories)
    for key, value in chart_inner_data.iteritems():
        json_entry = {'Category': key ,
                      'Hours': round(value['time'].seconds/float(3600) + value['time'].days*float(24), 2),
                      'Instances': str(value['count']),
                      'Color': value['color'],
                      }
        json_list[0].append(json_entry)

    # Return the data necessary for the outer ring of the double-donut chart (activities)
    for key, value in chart_outer_data.iteritems():
        json_entry = {'Activity': key ,
                      'Timeorder': count,
                      'Instances': str(value['count']),
                      'Hours': round(value['time'].seconds/float(3600) + value['time'].days*float(24), 2),
                      'Category': Activity.objects.get(activity_name=key).get_category_display()
                      }
        json_list[1].append(json_entry)
        count += 1

    # Also return the place or places so to pinpoint them on the Google Map
    if place_selected == "all" or place_selected == "Everywhere else":
        for p in user.places_set.all():
            json_list[3].append({
                'Place': p.place_name,
                'lat': p.place_lat,
                'lng': p.place_lng}
            )
    else:
        p = user.places_set.get(place_name=place_selected)
        json_list[3].append({
                'Place': p.place_name,
                'lat': p.place_lat,
                'lng': p.place_lng}
        )

    return HttpResponse(json.dumps(json_list), content_type='application/json')


def updateplacesbanner(request):
    user = request.user
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    place_selected = request.POST['place']
    radius_selected = request.POST['radius']
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment)

    total_time_spent_near_places = datetime.now() - datetime.now()
    total_activities_near_places = 0

    for activity_instance in instances:
        if activity_instance.location_address != "":
            if placesNearActivity(user, activity_instance, place_selected, radius_selected) != []:
                    total_time_spent_near_places += activity_instance.end_date - activity_instance.start_date
                    total_activities_near_places += 1
                    dummy_datetime_object = activity_instance

    try:
        dummy_datetime_object.start_date = datetime.now()
        dummy_datetime_object.end_date = datetime.now() + total_time_spent_near_places
        printable_time = dummy_datetime_object.displayable_date()
    except UnboundLocalError:
        printable_time = "0d0h0m"

    total_activities = len(instances)
    try:
        percentage_of_activities_near_places = round(total_activities_near_places/float(total_activities), 3)*100
    except ZeroDivisionError:
        percentage_of_activities_near_places = 0
    json_response = {
                    'total_activities': total_activities,
                    'total_activities_done_near_places': total_activities_near_places,
                    'percentage_of_activities_near_places': percentage_of_activities_near_places,
                    'total_time_spent_near_places': printable_time
                    }
    return HttpResponse(json.dumps(json_response),content_type="application/json")

##################################################################################

def updateallplacesbarchart(request):
    colourDict = {'black': "rgba(1, 1, 1, 0.8)",
                  'blue': "#578EBE",
                  'greenLight': "#99B433",
                  'orange': "#e09100",
                  'redDark': "rgb(148, 5, 37)",
                  'purple': "#800080"
    }
    user = request.user
    radius_selected = request.POST['radius']

    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment)
    all_places_data = {}
    json_list = []

    for activity_instance in instances:
        if activity_instance.location_address != "":
            places_that_contain_activity = placesNearActivity(user, activity_instance, 'all', radius_selected)
            if places_that_contain_activity != []:
                for place_name in places_that_contain_activity:
                    try:
                        all_places_data[place_name][activity_instance.activity.get_category_display()]['count'] += 1
                        all_places_data[place_name][activity_instance.activity.get_category_display()]['time'] += activity_instance.end_date - activity_instance.start_date
                    except KeyError:
                        try:
                            all_places_data[place_name]
                        except KeyError:
                            all_places_data[place_name] = {}
                        try:
                            all_places_data[place_name][activity_instance.activity.get_category_display()]
                        except KeyError:
                            all_places_data[place_name][activity_instance.activity.get_category_display()] = {}
                        all_places_data[place_name][activity_instance.activity.get_category_display()]['count'] = 1
                        all_places_data[place_name][activity_instance.activity.get_category_display()]['time'] = activity_instance.end_date - activity_instance.start_date
                        all_places_data[place_name][activity_instance.activity.get_category_display()]['color'] = colourDict[activity_instance.activity.category]
            else:
                try:
                    all_places_data["Everywhere else"][activity_instance.activity.get_category_display()]['count'] += 1
                    all_places_data["Everywhere else"][activity_instance.activity.get_category_display()]['time'] += activity_instance.end_date - activity_instance.start_date
                except KeyError:
                    try:
                        all_places_data["Everywhere else"]
                    except KeyError:
                        all_places_data["Everywhere else"] = {}
                    try:
                        all_places_data["Everywhere else"][activity_instance.activity.get_category_display()]
                    except KeyError:
                        all_places_data["Everywhere else"][activity_instance.activity.get_category_display()] = {}
                    all_places_data["Everywhere else"][activity_instance.activity.get_category_display()]['count'] = 1
                    all_places_data["Everywhere else"][activity_instance.activity.get_category_display()]['time'] = activity_instance.end_date - activity_instance.start_date
                    all_places_data["Everywhere else"][activity_instance.activity.get_category_display()]['color'] = colourDict[activity_instance.activity.category]

    for place_name, place_data in all_places_data.iteritems():
        for category_name, category_data in place_data.iteritems():
                json_entry = {'Place': place_name,
                              'Category': category_name ,
                              'Hours': round(category_data['time'].seconds/float(3600) + category_data['time'].days*float(24), 2),
                              'Instances': str(category_data['count']),
                              'Color': category_data['color'],
                              }
                json_list.append(json_entry)
    return HttpResponse(json.dumps(json_list), content_type='application/json')


def updateallactivitiescharts(request):
    colourDict = {'black': "rgba(1, 1, 1, 0.8)",
                  'blue': "#578EBE",
                  'greenLight': "#99B433",
                  'orange': "#e09100",
                  'redDark': "rgb(148, 5, 37)",
                  'purple': "#800080"
    }
    user = request.user
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment).order_by('activity__category')
    chart_outer_data = collections.OrderedDict()
    chart_inner_data = collections.OrderedDict()
    count = 1

    for activity_instance in instances:

        # Data for Activity Donut (outer)
        try:
            chart_inner_data[activity_instance.activity.get_category_display()]['count'] += 1
            chart_inner_data[activity_instance.activity.get_category_display()]['time'] += activity_instance.end_date - activity_instance.start_date
        except KeyError:
            chart_inner_data[activity_instance.activity.get_category_display()] = {}
            chart_inner_data[activity_instance.activity.get_category_display()]['count'] = 1
            chart_inner_data[activity_instance.activity.get_category_display()]['time'] = activity_instance.end_date - activity_instance.start_date
            chart_inner_data[activity_instance.activity.get_category_display()]['color'] = colourDict[activity_instance.activity.category]

        # Data for Category Donut (inner)
        try:
            chart_outer_data[activity_instance.activity.activity_name]['count'] += 1
            chart_outer_data[activity_instance.activity.activity_name]['time'] += activity_instance.end_date - activity_instance.start_date
        except KeyError:
            chart_outer_data[activity_instance.activity.activity_name] = {}
            chart_outer_data[activity_instance.activity.activity_name]['count'] = 1
            chart_outer_data[activity_instance.activity.activity_name]['time'] = activity_instance.end_date - activity_instance.start_date

    json_list = [[], []]
    for key, value in chart_inner_data.iteritems():
        json_entry = {'Category': key ,
                      'Hours': round(value['time'].seconds/float(3600) + value['time'].days*float(24), 2),
                      'Instances': str(value['count']),
                      'Color': value['color'],
                      }
        json_list[0].append(json_entry)

    for key, value in chart_outer_data.iteritems():
        json_entry = {'Activity': key ,
                      'Timeorder': count,
                      'Instances': str(value['count']),
                      'Interval': assignDurationInterval(value['time']),
                      'Hours': round(value['time'].seconds/float(3600) + value['time'].days*float(24), 2),
                      'Category': Activity.objects.get(activity_name=key).get_category_display()
                      }
        json_list[1].append(json_entry)
        count += 1

    return HttpResponse(json.dumps(json_list), content_type='application/json')

def updatesingleactivitycharts(request):
    user = request.user
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    activity_selected = request.POST['activity']
    activity_object = Activity.objects.get(activity_name=activity_selected)
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")
    instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment, activity=activity_object)

    dummy_iterator = range_first_moment
    timeaxis_activity_data = {}
    timeaxis_category_data = {}
    json_list = [[], []]
    while dummy_iterator < range_last_moment:
        timeaxis_activity_data[dummy_iterator.strftime("%m/%d/%Y")] = {}
        timeaxis_activity_data[dummy_iterator.strftime("%m/%d/%Y")]['count'] = 0
        timeaxis_activity_data[dummy_iterator.strftime("%m/%d/%Y")]['time'] = datetime.now() - datetime.now()

        timeaxis_category_data[dummy_iterator.strftime("%m/%d/%Y")] = {}
        timeaxis_category_data[dummy_iterator.strftime("%m/%d/%Y")]['count'] = 0
        timeaxis_category_data[dummy_iterator.strftime("%m/%d/%Y")]['time'] = datetime.now() - datetime.now()

        dummy_iterator += timedelta(days=1)

    # Data for Activity Series in Chart
    for activity_instance in instances:
        time_index = activity_instance.start_date
        while time_index < activity_instance.end_date:
            timeaxis_activity_data[time_index.strftime("%m/%d/%Y")]['count'] += 1

            done = False
            while not done:
                end_of_current_day = datetime.strptime(time_index.strftime("%m/%d/%Y") + ' 23:59:59', "%m/%d/%Y %H:%M:%S")
                if activity_instance.end_date <= end_of_current_day:
                    timeaxis_activity_data[time_index.strftime("%m/%d/%Y")]['time'] += activity_instance.end_date - activity_instance.start_date
                    done = True
                else:
                    timeaxis_activity_data[time_index.strftime("%m/%d/%Y")]['time'] += end_of_current_day - activity_instance.start_date
                    activity_instance.start_date = end_of_current_day + timedelta(seconds=1)
                time_index += timedelta(days=1)

    # Data for Category Series in Chart
    category_selected = activity_object.category
    category_instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment, activity__category=category_selected)
    for activity_instance in category_instances:
        time_index = activity_instance.start_date
        while time_index < activity_instance.end_date:
            timeaxis_category_data[time_index.strftime("%m/%d/%Y")]['count'] += 1

            done = False
            while not done:
                end_of_current_day = datetime.strptime(time_index.strftime("%m/%d/%Y") + ' 23:59:59', "%m/%d/%Y %H:%M:%S")
                if activity_instance.end_date <= end_of_current_day:
                    timeaxis_category_data[time_index.strftime("%m/%d/%Y")]['time'] += activity_instance.end_date - activity_instance.start_date
                    done = True
                else:
                    timeaxis_category_data[time_index.strftime("%m/%d/%Y")]['time'] += end_of_current_day - activity_instance.start_date
                    activity_instance.start_date = end_of_current_day + timedelta(seconds=1)
                time_index += timedelta(days=1)


    for key, value in timeaxis_activity_data.iteritems():
        json_list[0].append({
            'Date': key,
            'Series': activity_selected,
            'Instances': value['count'],
            'Hours': round(value['time'].seconds/float(3600) + value['time'].days*float(24), 2),
        })

    for key, value in timeaxis_category_data.iteritems():
        json_list[0].append({
            'Date': key,
            'Series': activity_object.get_category_display(),
            'Instances': value['count'],
            'Hours': round(value['time'].seconds/float(3600) + value['time'].days*float(24), 2),
        })

    # Here begins the code for the 2nd Chart -- the lineChart
    instances = instances.order_by('start_date')
    count = 1
    for activity_instance in instances:
        duration = activity_instance.end_date - activity_instance.start_date
        if activity_instance.goal != "":
            if activity_instance.goal_status == "Reached":
                goal_status_to_int = 3
            elif activity_instance.goal_status == "Failed":
                goal_status_to_int = 1
            else:
                goal_status_to_int = 2
        else:
            goal_status_to_int = 0

        json_list[1].append({
                               'Timeorder': count,
                               'Start_Date': activity_instance.start_date.strftime("%m/%d/%Y %H:%M"),
                               'Hours': round(duration.seconds/float(3600) + duration.days*float(24), 2),
                               'Goal_Status': goal_status_to_int
                              })
        count += 1

    return HttpResponse(json.dumps(json_list), content_type='application/json')


def updateactivitiesbanner(request):
    user = request.user
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    total_time_spent = datetime.now() - datetime.now()
    activity_selected = request.POST['activity']
    range_first_moment = datetime.strptime(datestart + '00:00:00', "%m/%d/%Y %H:%M:%S")
    range_last_moment = datetime.strptime(dateend + ' 23:59:59', " %m/%d/%Y %H:%M:%S")

    if activity_selected == "all":
        instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment)
        try:
            extra_mutable_analytic = round(len(instances.values('activity__activity_name').distinct())/float(len(instances)),3)*100
        except ZeroDivisionError:
            extra_mutable_analytic = 0
    else:
        activity_object = Activity.objects.get(activity_name=activity_selected)
        instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment, activity=activity_object)
        category_instances = user.performs_set.filter(start_date__lte=range_last_moment, end_date__gte=range_first_moment, activity__category=activity_object.category)
        try:
            extra_mutable_analytic = round(len(instances)/float(len(category_instances)), 3)*100
        except ZeroDivisionError:
            extra_mutable_analytic = 0


    for activity_instance in instances:
        total_time_spent += activity_instance.end_date - activity_instance.start_date
        dummy_datetime_object = activity_instance

    try:
        dummy_datetime_object.start_date = datetime.now()
        dummy_datetime_object.end_date = datetime.now() + total_time_spent
        printable_time = dummy_datetime_object.displayable_date()
    except UnboundLocalError:
        printable_time = "0d0h0m"

    total_activities = len(instances)
    json_response = {
                    'total_activities': total_activities,
                    'extra_mutable_analytic': extra_mutable_analytic,
                    'total_time_spent': printable_time
                    }
    return HttpResponse(json.dumps(json_response),content_type="application/json")


def social_login(request, action):

    action_parts = action.split('/')
    if action_parts[0] == 'sync':
        action = 'Sync'
        provider = action_parts[1]
    else:
        provider = None

    return render(request, 'activitytracker/social-login.html', {
        'action': action,
        'provider': provider
    })

def syncProviderActivities(request, provider):
    social_instance = request.user.social_auth.get(provider=provider)
    provider_object = eval(provider.title().replace('-', ''))(social_instance)

    return HttpResponse(provider_object.fetchData())


def routineSettings(request, setting='show'):

    def updateRoutine(user, routine_activity, time_string, day_type, delimiter, seasonality, db_setting):

        seasonality_parts = seasonality.split(' - ')
        seasonality_start, seasonality_end = seasonality_parts[0], seasonality_parts[1]
        seasonality_start_dateformat = None if not seasonality_start \
            else datetime.strptime(seasonality_start, "%m/%d").date()
        seasonality_end_dateformat = None if not seasonality_end \
            else datetime.strptime(seasonality_end, "%m/%d").date()

        if db_setting == 'edit':
            previous_instances = user.routine_set.filter(day_type=day_type, activity=routine_activity)
            for instance in previous_instances:
                instance.delete()

        if not time_string:
            return

        time_list = time_string.split(delimiter)

        for time_range in time_list:
            time_parts = time_range.split(' - ')
            start_time, end_time = time_parts[0], time_parts[1]
            start_datetimeformat = None if not start_time else datetime.strptime(start_time + ':00', "%H:%M:%S")
            end_datetimeformat = None if not end_time else datetime.strptime(end_time + ':00', "%H:%M:%S")

            instance = Routine(
                user=user,
                activity=routine_activity,
                start_time=start_datetimeformat,
                end_time=end_datetimeformat,
                day_type=day_type,
                seasonal_start=seasonality_start_dateformat,
                seasonal_end=seasonality_end_dateformat
            )
            instance.save()

        return

    user = request.user
    json_response = list()

    if setting == 'insert_more':

        for activity in Activity.objects.all().order_by('activity_name'):
            if activity.activity_name not in basic_routine_activities:
                json_response.append({
                    'activity': activity.activity_name,
                    'color': activity.category,
                    'icon_classname': activity.icon_classname,
                })

        return HttpResponse(
            json.dumps(json_response),
            content_type="application/json"
        )

    elif setting == "configure_periods":

        db_setting = request.POST['db_setting']
        activity_name = request.POST['activity']
        weekday_times = request.POST['weekday_times']
        weekend_times = request.POST['weekend_times']
        weekday_seasonality = request.POST['weekday_seasonality']
        weekend_seasonality = request.POST['weekend_seasonality']

        routine_activity = Activity.objects.get(activity_name=activity_name)

        updateRoutine(user, routine_activity, weekday_times, 'Weekdays', '_', weekday_seasonality, db_setting)
        updateRoutine(user, routine_activity, weekend_times, 'Weekend', '_', weekend_seasonality, db_setting)

        routine_activities = getFormattedRoutines(user, basic_routine_activities, day_types)

        return HttpResponse(
            json.dumps(routine_activities),
            content_type="application/json"
        )

    elif setting == "delete_routine":

        activity_name = request.POST['activity_name']
        activity = Activity.objects.get(activity_name=activity_name)
        for routine in user.routine_set.filter(activity=activity):
            routine.delete()

        if activity_name not in basic_routine_activities:
            return HttpResponse('RowRemoval')
        else:
            return HttpResponse('RowPersistance')


@login_required
def delete_account(request):
    if request.method == 'POST':

        # delete user and profile
        request.user.delete()

        return redirect('/')


def updateallroutinecharts(request):


    # This is a very slow function. The only way to increase speed is by integrating django 1.9 or reforming the database.
    # In this reform we have 2 options. Either split datetime into date & time fields (requires recoding the views.py)
    # , or add duplicate data on each save that will help isolate the query components better (but DUPLICATE THINGS WILL EXIST)

    user = request.user
    day_type_requested = request.POST['day_type']
    datestart = (request.POST['range']).split('-')[0]
    dateend = (request.POST['range']).split('-')[1]
    range_left = datetime.strptime(datestart, "%m/%d/%Y ").date()
    range_right = datetime.strptime(dateend, " %m/%d/%Y").date()
    chosen_start = datetime.strptime(datestart, "%m/%d/%Y ").date()
    chosen_end = datetime.strptime(dateend, " %m/%d/%Y").date()
    routine = request.POST['routine'].replace('-', ' ')
    routine_activity = Activity.objects.get(activity_name=routine)
    chart_data = collections.OrderedDict()
    routine_instances = dict()
    routine_instances['Weekdays'] = user.routine_set.filter(activity=routine_activity, day_type="Weekdays")
    routine_instances['Weekend'] = user.routine_set.filter(activity=routine_activity, day_type="Weekend")

    # Initialize a "visited" index in order to count each unique activity instance only once in total
    # regardless of the different routine logs overlapping its duration
    visited_ids = list()

    while True:

        # If we finished with all the days then break
        if range_left > range_right:
            break

        # Find out what type of day is the current day
        day_type = "Weekdays" if range_left.weekday() <= 4 else "Weekend"

        # If the day requested by the user is either "Weekend" or "Weekdays" (thus NOT full week), then if the current
        # day doesnt match the user's request, move to the next day
        if day_type_requested in ("Weekdays", "Weekend") and day_type_requested != day_type:
                range_left += timedelta(days=1)
                continue

        # If the current day_type doesnt hold any routine activities, move to the next day. Should break if both day
        # types were empty but the overhead is little at the moment
        if not routine_instances[day_type]:
            range_left += timedelta(days=1)
            continue

        background_actions = []
        # For each of the found routine instances (= different hours/seasonalities)
        for routine_instance in routine_instances[day_type]:

            # Check for assigned seasonality. If there is one, check if the current day belongs in this season. If not
            # then simply continue to the next day
            if (routine_instance.seasonal_start and routine_instance.seasonal_end) is not None:
                if not (routine_instance.seasonal_start < range_left < routine_instance.seasonal_end):
                    continue

            # Produce a datetime object (needed for 1.8 django) combining the current day and the times of the routine
            routine_start = datetime.combine(range_left, routine_instance.start_time)
            routine_end = datetime.combine(range_left, routine_instance.end_time)

            # Find the background activities that fall underneath the time span of the routine
            background_actions = user.performs_set.filter(
                start_date__lte=routine_end,
                end_date__gte=routine_start
            )

            for action in background_actions:

                # If we already checked this activity instance in a different iteration
                if action.id in visited_ids:
                    continue


                action_start = action.start_date
                action_end = action.end_date

                if (routine_start < action_start) and (routine_end > action_end) :
                    intersection_time = action_end - action_start
                    rest_time = action_end - action_end         # It is 0 of course

                elif (routine_start < action_start) and (routine_end <= action_end):
                    intersection_time = routine_end - action_start
                    rest_time = action_start - routine_start + action_end - routine_end

                elif (routine_start >= action_start) and (routine_end > action_end):
                    intersection_time = action_end - routine_start
                    rest_time = routine_start - action_start + routine_end - action_end

                else:
                    intersection_time = routine_end - routine_start
                    rest_time = routine_start - action_start + action_end - routine_end

                try:
                    chart_data[action.activity.activity_name]['count'] += 1
                    chart_data[action.activity.activity_name]['intersection_time'] += intersection_time
                    chart_data[action.activity.activity_name]['rest_time'] += rest_time

                except KeyError:
                    chart_data[action.activity.activity_name] = {}
                    chart_data[action.activity.activity_name]['count'] = 1
                    chart_data[action.activity.activity_name]['intersection_time'] = intersection_time
                    chart_data[action.activity.activity_name]['rest_time'] = rest_time

                # Add this ID to the visited list
                visited_ids.append(action.id)


        range_left += timedelta(days=1)

    json_list = []
    for key, value in chart_data.iteritems():


        json_entries = [

            {'Action': key ,
            'Instances': str(value['count']),
            'Hours': round(value['intersection_time'].seconds/float(3600) + value['intersection_time'].days*float(24), 2),
            'Timeslice': 'Routine Metric Overlap',
            'OrderByTime': round(value['intersection_time'].seconds/float(3600) + value['intersection_time'].days*float(24), 2),
            'OrderByInstances': str(value['count']),
            },
            {'Action': key ,
            'Instances': str(user.performs_set.filter(
                start_date__lte=chosen_end,
                end_date__gte=chosen_start,
                activity=Activity.objects.get(activity_name=key)
            ).count() - (value['count'])),
            'Hours': round(value['rest_time'].seconds/float(3600) + value['rest_time'].days*float(24), 2),
            'Timeslice': 'Routine Metric Disjointedness',
            'OrderByTime': round(value['intersection_time'].seconds/float(3600) + value['intersection_time'].days*float(24), 2),
            'OrderByInstances': str(value['count']),
            },
        ]
        json_list += json_entries

    return HttpResponse(json.dumps(json_list), content_type='application/json')
