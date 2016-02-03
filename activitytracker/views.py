from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout, login as auth_login, authenticate
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

    if request.method != 'POST':
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('dashboard'))

        return render(request,
                      'activitytracker/login.html',
                      {'redirect_url': request.GET.get('next',
                                                       '/activitytracker/dashboard'
                                                       )
                       }
                      )

    username_or_email = request.POST['username']
    password = request.POST['password']

    if User.objects.filter(username__iexact=username_or_email).count() == 0:

        if User.objects.filter(email__iexact=username_or_email).count() == 0:
            return HttpResponseBadRequest(INVALID_CREDENTIALS_MSG)
        else:
            username = User.objects.get(email__iexact=username_or_email).username

    else:
        username = username_or_email

    user = authenticate(username=username, password=password)

    if user is None:
        return HttpResponseBadRequest(INVALID_CREDENTIALS_MSG)

    if not user.is_active:
        return HttpResponseBadRequest(EMAIL_VERIFICATION_MSG)

    auth_login(request, user)

    return HttpResponse('Ok')


# Flush Session and redirect
def logout(request):

    auth_logout(request)
    return HttpResponseRedirect(reverse('login'))


# Check and Register the User
def register(request):

    EMAIL_EXISTS_MSG = 'EmailExists'
    EMPTY_FIELDS_MSG = 'EmptyFields'
    PASSWORD_ERROR = 'PasswordMismatch'
    SUCCESS_MSG = 'Registration Successful! ' \
                  'We have sent you an e-mail with a validation link to follow'

    if request.method != 'POST':
        return render(request, 'activitytracker/register.html')

    email = request.POST['email']
    password = request.POST['password']
    repeated_password = request.POST['password_repeat']

    if User.objects.filter(email__iexact=email).exists():
        return HttpResponseBadRequest(EMAIL_EXISTS_MSG)

    if password != repeated_password:
        return HttpResponseBadRequest(PASSWORD_ERROR)

    if '' in (email, password, repeated_password):
        return HttpResponseBadRequest(EMPTY_FIELDS_MSG)

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

    email = "Activitytracker.app@gmail.com"
    mail_title = "Activity Tracker Account Verification"
    recipient = [user.email.encode('utf8')]
    mail_message = 'Hello user %s. In order to verify your account click the following link: %s' \
                   % (user.get_username(), verification_url)

    send_mail(mail_title, mail_message, email, recipient, fail_silently=False)

    return HttpResponse(SUCCESS_MSG)


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

    email = "Activitytracker.app@gmail.com"
    mail_title = "Activity Tracker Password Reset"
    recipient = [user.email.encode('utf8')]
    mail_message = 'Hello user %s. You have recently requested a password reset. Please follow this link in order to ' \
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


# Deletes an activity
def deleteactivity(request, performs_id):

    activity = Performs.objects.get(id=performs_id)
    activity.delete()

    return HttpResponse('Deleted')


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
        return HttpResponseBadRequest(FIELD_ERROR_MSG)

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


def social_login(request, action):
    return render(request, 'activitytracker/social-login.html',{'action': action})


def syncProviderActivities(request, provider):
    social_instance = request.user.social_auth.get(provider=provider)
    provider_object = eval(provider.title().replace('-', ''))(social_instance)

    return HttpResponse(provider_object.fetchData())


# Handle settings options
@login_required
def settings_page(request):

    user = request.user
    providerDomValues = {}

    for provider in AVAILABLE_PROVIDERS:

        if user.social_auth.filter(provider=provider).count() == 0:
            providerDomValues[provider] = getAppManagementDomValues("Not Connected", provider)
            continue

        provider_object = eval(provider.title().replace('-', ''))(user.social_auth.get(provider=provider))
        providerDomValues[provider] = getAppManagementDomValues(provider_object.validate(), provider)

    context = {
               'providerDomValues': providerDomValues
               }

    return render(request, 'activitytracker/settings.html', context)
