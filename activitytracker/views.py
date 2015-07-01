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
import string
import random
import json
import calendar
import operator
import collections
import requests
from myfunctions import *
from datetime import datetime

# Terms and Conditions page

def terms_and_conditions(request):
    return render(request, 'activitytracker/terms_and_conditions.html', {})

# Page that logs in the user + Checks
def login(request):
    if request.method != 'POST':
        if not request.user.is_authenticated():
            return render(request, 'activitytracker/login.html',{'redirect_url': request.GET.get('next','/activitytracker/index')})
        else:
            return HttpResponseRedirect(reverse('index'))

    username = request.POST['username']
    password = request.POST['password']
    try:
        User.objects.get(username=username)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                if user.last_login is None:
                    user_type = "NewUser"
                else:
                    user_type = "OldUser"
                auth_login(request, user)
                return HttpResponse(user_type)
            else:
                return HttpResponseBadRequest("You need to verify your E-mail in order to log in!")
        else:
            return HttpResponseBadRequest("Wrong Combination of Username and Password")
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("No such User exists")



# Flush Session and redirect
def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('login'))


# Check and Register the User (check is done here due to incompatability with AJAX)
def register(request):
    if request.method != 'POST':
        return render(request, 'activitytracker/register.html')

    username = request.POST['username']
    if User.objects.filter(username__iexact=username).exists():
        return HttpResponseBadRequest("1")

    email = request.POST['email']
    if User.objects.filter(email__iexact=email).exists():
        return HttpResponseBadRequest("2")

    passw = request.POST['password']
    firstname = request.POST['firstname']
    lastname = request.POST['lastname']
    gender = request.POST['gender']
    bday = request.POST['birthday']
    if bday == "" or username == "" or firstname == "" or lastname == "" or email == "" or passw == "":
        return HttpResponseBadRequest("4")

    birthday = datetime.strptime(request.POST['birthday'], "%m/%d/%Y").date()
    if birthday > datetime.now().date():
        return HttpResponseBadRequest('3')

    user = User.objects.create_user(username, email, passw, first_name=firstname, last_name=lastname, gender=gender, date_of_birth=birthday)
    user.is_active = False
    user.save()
    size = 20
    characters = string.ascii_letters + string.digits
    random_verification_code = ''.join(random.choice(characters) for _ in range(size))
    verification_url = 'http://127.0.0.1:8000/activitytracker/account/verification/' + random_verification_code
    verification_instance = UserVerification(user=user, verification_code=random_verification_code)
    verification_instance.save()
    mail_title = "Activity Tracker Account Verification"
    mail_message = 'Hello user '+ user.get_username() + '.In order to verify your account click the following link: ' + verification_url
    email = "Activitytracker.app@gmail.com"
    recipient = [user.email.encode('utf8')]
    send_mail(mail_title, mail_message, email, recipient, fail_silently=False)
    return HttpResponse('Registration successful! We have sent you an e-mail with a link to verify your e-mail (can be marked as Spam)')


# Produce random pass and send it with e-mail
def passwordforget(request):

    if request.method != 'POST':
        return render(request, 'activitytracker/passforget.html')

    user = request.POST['username']
    try:
        user = User.objects.get(username=user)
        size = 8
        characters = string.ascii_lowercase + string.digits
        new_pass = ''.join(random.choice(characters) for _ in range(size))
        user.set_password(new_pass)
        user.save()
        mail_title = "Password Reset"
        mail_message = 'You have recently forgot your password. Your new password is: ' + new_pass + ' which you can ' \
           'always change it through your account options.\n Please do not reply to this message.\n Always at your' \
           ' disposal,\n Activity Tracker Support Team'
        email = "Activitytracker.app@gmail.com"
        recipient = [user.email.encode('utf8')]
        send_mail(mail_title, mail_message, email, recipient, fail_silently=False)
        return HttpResponse('We have sent you an E-mail with a temporary password. You will now be redirected'
                            ' to the Login Page.')
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Sorry no such User exists")


# view to handle the email verification
def email_verification(request, verification_code):
    try:
        verification_instance = UserVerification.objects.get(verification_code=verification_code)
        user = verification_instance.user
        user.is_active = True
        user.save()
        verification_instance.delete()
        verification_successful = True
    except ObjectDoesNotExist:
        verification_successful = False
    return render(request,'activitytracker/account-verification.html',{'verification_successful': verification_successful})



# Handle settings options
@login_required
def settings(request):
    user = request.user

    if request.method == 'POST':
        if request.POST['settingAction'] == 'deleteaccount':
            curr_password = request.POST['password']
            if user.check_password(curr_password):
                user.delete()
                return HttpResponseRedirect(reverse('login'))
            else:
                return HttpResponseBadRequest("The password you have entered didn't match your current password")
        elif request.POST['settingAction'] == 'editinfo':
                user.username = request.POST['username']
                user.first_name = request.POST['firstname']
                user.last_name = request.POST['lastname']
                user.gender = request.POST['gender']
                if request.POST['birthday'] == "" or user.first_name == "" or user.last_name == "":
                    return HttpResponseBadRequest("Cannot update with empty fields")
                try:
                    if user != User.objects.get(username=request.POST['username']):
                        return HttpResponseBadRequest("Username already exists. Try another")
                except ObjectDoesNotExist:
                    pass
                user.date_of_birth = datetime.strptime(request.POST['birthday'], "%m/%d/%Y").date()

                if user.date_of_birth < datetime.now().date():
                    user.save()
                    return HttpResponse(
                                        json.dumps(
                                            {
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
                else:
                    return HttpResponseBadRequest("You can't be born in the future dude...")
        elif request.POST['settingAction'] == 'passchange':
            if request.POST['new_password'] != request.POST['new_password_repeat']:
                return HttpResponseBadRequest("Sorry the new passwords you entered didn't match each other")

            if user.has_usable_password():
                if not user.check_password(request.POST['old_password']):
                    return HttpResponseBadRequest("Sorry the password you entered is not your current password")

            user.set_password(request.POST['new_password'])
            user.save()
            return HttpResponseRedirect(reverse('login'))

    if user.gender == None:
        gender = ''
    else:
        gender = user.gender
    if user.date_of_birth == None:
        birth = ''
    else:
        birth = user.date_of_birth.strftime("%m/%d/%Y")

    providerDomValues = {}
    for provider_name in available_providers:
        providerDomValues[provider_name] = getAppManagementDomValues(checkConnection(user, provider_name), provider_name)

    context = {'username': user.get_username(),
               'firstname': user.get_short_name(),
               'lastname': user.last_name,
               'email': user.email,
               'birth': birth,
               'gender': gender,
               'social_login': not user.has_usable_password(),
               'providerDomValues': providerDomValues
               }
    return render(request, 'activitytracker/settings.html', context)

# Handler for the Places in Settings.html
@login_required
def places(request):
    user = request.user

    if request.method != "POST":
        return HttpResponseRedirect(reverse('settings'))

    if request.POST['setting'] == "addPlace" or request.POST['setting'] == "editPlace":
        name = request.POST['place_name']
        address = request.POST['address']
        lat = request.POST['lat']
        lng = request.POST['lng']
        if name == "":
            return HttpResponseBadRequest('Empty')

        if request.POST['setting'] == "addPlace":
            a = Places(user=user, place_name=name, place_address=address, place_lat=lat, place_lng=lng)
        else:
            place_id = request.POST['place_id']
            a = user.places_set.get(place_id=place_id)
            a.place_name = name
            a.place_address = address
            a.place_lat = lat
            a.place_lng = lng

        try:
            a.save()
            return HttpResponse('ok')
        except IntegrityError:
            return HttpResponseBadRequest('Unique')

    elif request.POST['setting'] == "deletePlace":
        id_to_del = request.POST['place_id']
        place = user.places_set.get(place_id=id_to_del)
        place.delete()
        return HttpResponse('ok')


def placestojson(request):
    user = request.user
    places = user.places_set.all()
    json_list = {"data": []}
    for p in places:
        json_entry = {'id': p.place_id,
                      'lat': p.place_lat,
                      'lng': p.place_lng,
                      'place_name': p.place_name,
                      'place_address': p.place_address
        }
        json_list['data'].append(json_entry)
    return HttpResponse(json.dumps(json_list), content_type='application/json')



# Basic View, Gets called on "History" page load
@login_required
def index(request, user_type="RegisteredUser"):
    user = request.user
    object_list = [i.object_name for i in user.object_set.all()] #for form
    friend_list = [i.friend_name for i in user.friend_set.all()] #for form
    goal_list = [i.goal for i in user.performs_set.exclude(goal__exact='')] #for form

    colourdict = {'black': 0, 'blue': 1, 'greenLight': 2,
                  'orange': 3, 'redDark': 4, 'purple': 5 }
    act_name_list = Activity.objects.values('activity_name', 'category').order_by('activity_name').distinct()
    activity_context_list = [[],[],[],[],[],[]]
    for activity in act_name_list:
        list_to_append = activity_context_list[colourdict[activity['category']]]
        list_to_append.append(activity['activity_name'])

    activity_data = {
                    "Selfcare/Everyday Needs": activity_context_list[0],
                    "Communication/Socializing": activity_context_list[1],
                    "Sports/Fitness": activity_context_list[2],
                    "Fun/Leisure/Hobbies": activity_context_list[3],
                    "Responsibilities": activity_context_list[4],
                    "Transportation": activity_context_list[5],
                   }

    if user_type == "NewUser":
        show_carousel_guide = True
    else:
        show_carousel_guide = False
    context = {'list_of_objects': object_list,
               'username': user.get_username(),
               'list_of_friends': friend_list,
               'list_of_goals': goal_list,
               'activity_data': activity_data,
               'show_carousel_guide': show_carousel_guide
               }




    return render(request, 'activitytracker/index.html', context)

# Gets called on "Group common" click, to return grouped activities
def getgroupedactivities(request):
    user = request.user
    if len(request.POST['grouped_data']) > 0:
        ids = (request.POST['grouped_data'])[1:].split("_")
    else:
        return HttpResponse(json.dumps([]), content_type='application/json')

    instances = user.performs_set.filter(id__in=ids)
    json_list = []
    if request.POST['box'] == "checked":
        ordered = instances.order_by('activity')
        for index, i in enumerate(ordered):
            if index == 0:
                event = i
                grouped_id = str(i.id);
            elif i.activity != prev_i.activity:
                json_entry = {'id': grouped_id,
                              'duration': event.displayable_date(),
                              'start_date': event.start_date.strftime('%Y%m%d%H%M'),
                              'activity': event.activity.activity_name,
                              'colour': str(event.activity.category),
                              'icon_classname': event.activity.icon_classname
                        }
                json_list.append(json_entry)
                event = i
                grouped_id = str(i.id);
            else:
                event.end_date += i.end_date - i.start_date
                grouped_id = grouped_id + '_' + str(i.id)
            prev_i = i
        #######################
        json_entry = {  'id': grouped_id,
                        'duration': event.displayable_date(),
                        'start_date': event.start_date.strftime('%Y%m%d%H%M'),
                        'activity': event.activity.activity_name,
                        'colour': str(event.activity.category),
                        'icon_classname': event.activity.icon_classname
                     }
        json_list.append(json_entry)
    else:
        for event in instances:
            json_entry = {  'id': event.id,
                            'start_date': event.start_date.strftime('%Y%m%d%H%M'),
                            'duration': event.displayable_date(),
                            'activity': event.activity.activity_name,
                            'colour': str(event.activity.category),
                            'icon_classname': event.activity.icon_classname
                         }
            json_list.append(json_entry)
    sort = request.POST['sort']
    if sort == "Activity":
        dummy = sorted(json_list, key=operator.itemgetter('activity', 'start_date'))
    elif sort == "Category":
        dummy = sorted(json_list, key=operator.itemgetter('colour', 'start_date'))
    else:
        dummy = sorted(json_list, key=operator.itemgetter('start_date'))
    json_list = dummy
    return HttpResponse(json.dumps(json_list), content_type='application/json')


# Gets called each time an activity is added
def addactivity(request):
    user = request.user
    act_name = request.POST['name_of_activity']
    try:
        the_activity = Activity.objects.get(activity_name=act_name)
    except Activity.DoesNotExist:
        return HttpResponseBadRequest('Invalid Activity Input. Please try again')
    start_datetime = request.POST['start_date'] + " " + request.POST['start_time'] + ":00"
    end_datetime = request.POST['end_date'] + " " + request.POST['end_time'] + ":00"
    the_goal = request.POST['goal']
    the_result = request.POST['result']
    friendlist = request.POST['friend_list']
    object_list = request.POST['tool'].split(",")
    friends = request.POST['friend_list'].split(",")
    location_address = request.POST['location_address']
    lat = request.POST['lat']
    lng = request.POST['lng']
    if not lat:
        lat = lng = None
    try:
        start_datetimeformat = datetime.strptime(start_datetime, "%m/%d/%Y %H:%M:%S")
        end_datetimeformat = datetime.strptime(end_datetime, "%m/%d/%Y %H:%M:%S")
    except ValueError:
        return HttpResponseBadRequest('Please fill up at least Date and Time fields correctly')
    if start_datetimeformat > end_datetimeformat:
        return HttpResponseBadRequest("Activity can't end sooner than it started. Please try again")

    for f in friends:
        try:
            user.friend_set.get(friend_name=f.lstrip(' '))
        except ObjectDoesNotExist:
            a = Friend(friend_name=f.lstrip(' '), friend_of_user=user)
            if a.friend_name != "":
                a.save()

    for o in object_list:
        try:
            user.object_set.get(object_name=o.lstrip(' '))
        except ObjectDoesNotExist:
            a = Object(object_name=o.lstrip(' '), object_of_user=user)
            if a.object_name != "":
                a.save()

    try:
        a = Performs(user=user, activity=the_activity, goal=the_goal, result=the_result, start_date=start_datetimeformat,
            end_date=end_datetimeformat, friends=friendlist, location_address=location_address, location_lat=lat, location_lng=lng)
        a.save()
        if the_goal != "":
            a.goal_status = request.POST['goalstatus']
            a.save()
    except ValueError:
        return HttpResponseBadRequest('Database insertion Error. Please check your fields and try again')


    for o in object_list:
        if o != "":
            object_used = Object.objects.get(object_name=o)
            a.using.add(object_used)

    return HttpResponse(
        json.dumps(
            {
                'id': str(a.id),
                'duration': a.displayable_date(),
                'activity': a.activity.activity_name,
                'colour': str(a.activity.category)
            }
        ),
        content_type='application/json'
    )


# Gets called each time a single activity is clicked
def showactivity(request, performs_identification):
    colourDict = {'black': "rgba(1, 1, 1, 0.8)",
                  'blue': "#578EBE",
                  'greenLight': "#99B433",
                  'orange': "#e09100",
                  'redDark': "#850521",
                  'purple': "#800080"
    }
    user = request.user
    details = user.performs_set.get(id=performs_identification)
    tools = details.using.all()
    tools_string = ', '.join(str(t.object_name) for t in tools)
    start_date = details.start_date.strftime('%m/%d/%Y')
    end_date = details.end_date.strftime('%m/%d/%Y')
    end_time = details.end_date.strftime('%H:%M')
    start_time = details.start_date.strftime('%H:%M')
    context = {'instance': details, 'tools': tools_string, 'start_t': start_time, 'end_t': end_time,
               'end_date': end_date, 'start_date': start_date, 'color': colourDict[details.activity.category] }
    return SimpleTemplateResponse('activitytracker/display-activity.html', context)

# Gets called when a grouped activity needs to be shown
def showgroupactivity(request, group_identification):
    colourDict = {'black': "rgba(1, 1, 1, 0.8)",
                  'blue': "#578EBE",
                  'greenLight': "#99B433",
                  'orange': "#e09100",
                  'redDark': "#850521",
                  'purple': "#800080"
    }
    id_list = group_identification.split('_')
    user = request.user
    events = user.performs_set.filter(id__in=id_list).order_by('start_date')
    context_list = []
    for details in events:
        tools_string = ', '.join(str(t.object_name) for t in details.using.all())
        start_date = details.start_date.strftime('%m/%d/%Y')
        end_date = details.end_date.strftime('%m/%d/%Y')
        start_time = details.start_date.strftime('%H:%M')
        end_time = details.end_date.strftime('%H:%M')
        context_list.append({'tools': tools_string,
                             'start_time': start_time,
                             'end_time': end_time,
                             'end_date': end_date,
                             'start_date': start_date,
                             'instance': details,
                             })
    colour = colourDict[Performs.objects.get(id=id_list[0]).activity.category]
    context = { 'activity_list': context_list, 'color': colour, 'total_grouped_activities': len(id_list) }
    return SimpleTemplateResponse('activitytracker/display-group-activity.html', context)

# Deletes an activity
def deleteactivity(request):

    the_id = request.POST['act_id']
    act = Performs.objects.get(id=the_id)
    act.delete()
    return HttpResponse('Deleted')

# Gives all the activities as JSON
@login_required
def listallactivities(request):
    context = {'activity_list': Activity.objects.all()}
    return render(request, 'activitytracker/activitytable.html', context)



#Gets called when Edit button is clicked, to instantiate values of inputs in the template
def editactivity(request, performs_id):
    colourDict = {'black': "rgba(1, 1, 1, 0.8)",
                  'blue': "#578EBE",
                  'greenLight': "#99B433",
                  'orange': "#e09100",
                  'redDark': "#850521",
                  'purple': "#800080"
    }
    user = request.user
    details = Performs.objects.get(id=int(performs_id))
    start_date = details.start_date.strftime('%m/%d/%Y')
    end_date = details.end_date.strftime('%m/%d/%Y')
    end_time = details.end_date.strftime('%H:%M')
    start_time = details.start_date.strftime('%H:%M')

    instance_object_list = [i.object_name for i in details.using.all()]
    object_list = [i.object_name for i in user.object_set.all()] #for form
    instance_friend_list = filter(None, details.friends.split(","))
    friend_list = [i.friend_name for i in user.friend_set.all()] #for form
    goal_list = [i.goal for i in user.performs_set.exclude(goal__exact='')] #for form
    category_dict = {'black': 0, 'blue': 1, 'greenLight': 2,
                  'orange': 3, 'redDark': 4, 'purple': 5 }

    act_name_list = Activity.objects.values('activity_name', 'category').order_by('activity_name').distinct()
    activity_context_list = [[],[],[],[],[],[]]
    for activity in act_name_list:
        list_to_append = activity_context_list[category_dict[activity['category']]]
        list_to_append.append(activity['activity_name'])

    activity_data = {
                    "Selfcare/Everyday Needs": activity_context_list[0],
                    "Communication/Socializing": activity_context_list[1],
                    "Sports/Fitness": activity_context_list[2],
                    "Fun/Leisure/Hobbies": activity_context_list[3],
                    "Responsibilities": activity_context_list[4],
                    "Transportation": activity_context_list[5],
                   }


    context = {'instance': details,
               'instance_object_list': instance_object_list,
               'instance_friend_list': instance_friend_list,
               'start_t': start_time,
               'end_t': end_time,
               'end_date': end_date,
               'start_date': start_date,
               'activity_data': activity_data,
               'list_of_objects': object_list,
               'list_of_friends': friend_list,
               'list_of_goals': goal_list,
               'color': colourDict[details.activity.category],
    }

    return SimpleTemplateResponse('activitytracker/edit-activity.html', context)


#Gets called on update activity
def updateactivity(request):
    user = request.user
    the_id = request.POST['the_id']
    details = Performs.objects.get(id=int(the_id))
    activity = request.POST['name_of_activity']
    location_address = request.POST['location_address']
    lat = request.POST['lat']
    lng = request.POST['lng']
    try:
        details.activity = Activity.objects.get(activity_name=activity)
    except Activity.DoesNotExist:
        return HttpResponseBadRequest('Invalid Activity Input. Please try again')

    end_date = request.POST['end_date'] + " " + request.POST['end_time'] + ":00"
    start_date = request.POST['start_date'] + " " + request.POST['start_time'] + ":00"
    try:
        details.end_date = datetime.strptime(end_date, "%m/%d/%Y %H:%M:%S")
        details.start_date = datetime.strptime(start_date, "%m/%d/%Y %H:%M:%S")
        if details.start_date > details.end_date:
            return HttpResponseBadRequest("Activity can't end sooner than it started. Please try again")
    except ValueError:
        return HttpResponseBadRequest('Please fill up at least Date and Time fields correctly')

    details.friends = ','.join(list(set(request.POST['friend_list'].split(','))))
    details.location_address = location_address
    details.location_lat = lat
    details.location_lng = lng

    details.goal = request.POST['goal']
    details.result = request.POST['result']
    if details.goal != "":
        details.goal_status = request.POST['goalstatus']
    else:
        details.goal_status = None

    friends = request.POST['friend_list'].split(",")
    for f in friends:
        try:
            user.friend_set.get(friend_name=f.lstrip(' '))
        except ObjectDoesNotExist:
            a = Friend(friend_name=f.lstrip(' '), friend_of_user=user)
            if a.friend_name != "":
                a.save()

    object_list = request.POST['tool'].split(",")
    for o in object_list:
        try:
            user.object_set.get(object_name=o.lstrip(' '))
        except ObjectDoesNotExist:
            a = Object(object_name=o.lstrip(' '), object_of_user=user)
            if a.object_name != "":
                a.save()

    try:
        details.save()
    except ValueError:
        return HttpResponseBadRequest('Database insertion Error. Please check your fields and try again')

    for previous_obj in details.using.all():
        details.using.remove(previous_obj)

    for o in object_list:
        if o != "":
            object_used = Object.objects.get(object_name=o)
            details.using.add(object_used)

    date_format = details.start_date.strftime('%I:%M%p (%m/%d/%Y)')
    return HttpResponse(
        json.dumps(
            {
                'id': str(details.id),
                'duration': details.displayable_date(),
                'activity': details.activity.activity_name,
                'colour': str(details.activity.category),
                'start_date': str(date_format),
                'goal': details.goal,
                'goal_status': details.goal_status,
                'friends': details.friends,
                'location_address': details.location_address,
                'tools': ', '.join(str(t.object_name) for t in details.using.all()),
                'icon_classname': details.activity.icon_classname,

            }
        ),
        content_type='application/json'
    )

# provides the JSON to the chart of Index Page
def chartdatajson(request):
    user = request.user
    if len(request.GET['chart_data']) > 0:
        ids = (request.GET['chart_data'])[1:].split("_")
    else:
        return HttpResponse(json.dumps([]), content_type='application/json')
    colourdict = {'black': 0, 'blue': 1, 'greenLight': 2,
                  'orange': 3, 'redDark': 4, 'purple': 5 }
    durations = [0, 0, 0, 0, 0, 0]
    for event_id in ids:
            entry = user.performs_set.get(id=int(event_id))
            dur = entry.end_date - entry.start_date
            minutes = dur.seconds/60 + dur.days*24*60
            durations[colourdict[entry.activity.category]] += minutes
    json_list = [{'label': "Selfcare/Everyday Needs",  'data': durations[0], 'color': "rgba(1, 1, 1, 0.9)"},
                 {'label': "Communication/Socializing",  'data': durations[1], 'color': "#1b0297"},
                 {'label': "Sports/Fitness",  'data': durations[2], 'color': "#99B433"},
                 {'label': "Fun/Leisure/Hobbies",  'data': durations[3], 'color': "#e09100"},
                 {'label': "Responsibilities",  'data': durations[4], 'color': "#850521"},
                 {'label': "Transportation",  'data': durations[5], 'color': "#800080"}
                 ]
    return HttpResponse(json.dumps(json_list), content_type='application/json')

# Provides the event to the calendar
def eventstojson(request):

    colourdict= {'black': "rgba(1, 1, 1, 0.9)",
                 'orange': "#e09100",
                 'purple': "purple",
                 'blue': "#1b0297",
                 'redDark': "#850521",
                 'greenLight': "#99B433"
                }
    user = request.user
    allevents = user.performs_set.all()

    json_list = []
    for event in allevents:
        the_id = event.id
        title = event.activity.activity_name
        start = event.start_date.strftime("%Y-%m-%dT%H:%M:%S")
        end = event.end_date.strftime("%Y-%m-%dT%H:%M:%S")
        allDay = False
        editable = False
        colour = colourdict[event.activity.category]
        json_entry = {'id': the_id,
                      'start': start,
                      'allDay': allDay,
                      'end': end,
                      'editable': editable,
                      'title': title,
                      'color': colour,
                    }
        json_list.append(json_entry)
    return HttpResponse(json.dumps(json_list), content_type='application/json')

# Gets called when calendar changes view
def displayperiod(request):

    user = request.user

    monthDict = {'Jan': 1, 'Feb': 2, 'Mar': 3,
                 'Apr': 4,  'May': 5,   'Jun': 6,
                 'Jul': 7,  'Aug': 8,   'Sep': 9,
                 'Oct': 10,  'Nov': 11,   'Dec': 12,
                 }
    mode = request.POST['mode']
    if mode == "month":
        year = request.POST['year']


        month = request.POST['month']


        month_last_moment = datetime.strptime(year + '-' + month + '-' + str(calendar.monthrange(int(year),
                                                         int(monthDict[month]))[1]) + ' 23:59:59',"%Y-%b-%d %H:%M:%S")
        month_first_moment = datetime.strptime(year + '-' + month + '-01 00:00:00', "%Y-%b-%d %H:%M:%S")
        instances = user.performs_set.filter(start_date__lte=month_last_moment, end_date__gte=month_first_moment)
    elif mode == "agendaDay":
        day = request.POST['day']
        year = request.POST['year']
        month = request.POST['month']

        day_last_moment = datetime.strptime(year + '-' + month + '-' + day + ' 23:59:59', "%Y-%b-%d %H:%M:%S")
        day_first_moment = datetime.strptime(year + '-' + month + '-' + day + ' 00:00:00', "%Y-%b-%d %H:%M:%S")
        instances = user.performs_set.filter(start_date__lte=day_last_moment, end_date__gte=day_first_moment)
    else:
        day = request.POST['day']
        year = request.POST['year']
        month = request.POST['month']

        day2 = request.POST['day2']
        year2 = request.POST['year2']
        month2 = request.POST['month2']

        week_first_moment = datetime.strptime(year + '-' + month + '-' + day + ' 00:00:00', "%Y-%b-%d %H:%M:%S")
        week_last_moment = datetime.strptime(year2 + '-' + month2 + '-' + day2 + ' 23:59:59', "%Y-%b-%d %H:%M:%S")
        instances = user.performs_set.filter(start_date__lte=week_last_moment, end_date__gte=week_first_moment)

    responseString = ""
    for event in instances:
        responseString = responseString + "_" + str(event.id)
    return HttpResponse(responseString)


# Called to instantiate HTML and redirect to Goals Page
@login_required
def goals(request):
    user = request.user
    total_goals = len(user.performs_set.exclude(goal=""))
    return render(request, 'activitytracker/goals.html', {'username': user.get_username(), 'total_number': total_goals})


# Feeds the jQuery.dataTable that is the table in the Goals page
def goalstojson(request):
    user = request.user
    activities = user.performs_set.exclude(goal="")
    json_list = {"data": []}
    for a in activities:
        if a.goal != "":
            json_entry = {'goal': a.goal,
                          'date': a.start_date.strftime('%m/%d/%Y'),
                          'activity': a.activity.activity_name,
                          'goal_status': a.goal_status,
                          'id': a.id,
            }
            json_list['data'].append(json_entry)
    return HttpResponse(json.dumps(json_list), content_type='application/json')


# Gets called when any action from Goals.html is being performed
def goalhandler(request):
    user = request.user
    setting = request.POST['setting']
    if setting == "deleteGoal":
        deletegoal_id = request.POST['performs_id']
        performs_instance = user.performs_set.get(id=deletegoal_id)
        performs_instance.goal, performs_instance.goal_status = "", None
        performs_instance.save()
        return HttpResponse(len(user.performs_set.exclude(goal="")))
    elif setting == "updateGoal":
        updatedgoal = request.POST['data']
        updatedgoal_id = request.POST['performs_id']
        if updatedgoal == "":
            return HttpResponseBadRequest("Goal can't be empty! If you want to delete it you can do so through options.")
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
    tools_string = ', '.join(str(t.object_name) for t in details.using.all())
    json_list = {'id': details.id,
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
    user = request.user
    return render(request, 'activitytracker/timeline.html',{'username':user.get_username()})

 # Feeds the activities as json and paginates them to the html
def timeline_events_json(request):
    user = request.user

    total_events = user.performs_set.order_by('-start_date')
    paginator = Paginator(total_events, 10)

    requested_page = request.GET['page']
    try:
        json_list = []
        requested_events = paginator.page(requested_page)
        for details in requested_events:
            tools_string = ', '.join(str(t.object_name) for t in details.using.all())
            start_date = details.start_date.strftime('%I:%M%p (%m/%d/%Y)')
            json_entry = { 'activity': details.activity.activity_name,
                           'start_date': str(start_date),
                           'duration': details.displayable_date(),
                           'goal': details.goal,
                           'goal_status': details.goal_status,
                           'friends': details.friends,
                           'tools': tools_string,
                           'result': details.result,
                           'colour': details.activity.category,
                           'id': details.id,
                           'location_address': details.location_address,
                           'icon_classname': details.activity.icon_classname,
            }
            json_list.append(json_entry)
    except EmptyPage:
        pass
    return HttpResponse(json.dumps(json_list), content_type='application/json')


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
    return render(request, 'activitytracker/social-login.html',{'action': action})

def syncProviderActivities(request, provider):
    user = request.user
    if checkConnection(user, provider) in ("Not Connected", "Authentication Failed"):
        return HttpResponseBadRequest("Provider not connected or authorized properly. " +
                                      "Please visit your profile page to resolve the issue")

    return providerSyncFunctions[provider](user)
