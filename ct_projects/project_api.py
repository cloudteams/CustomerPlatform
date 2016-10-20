from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ct_projects.forms import ProjectForm
from ct_projects.models import Project, PollToken, Campaign, Poll, Document

from copy import deepcopy
import json
import thread

__author__ = 'dipap'


def field_translation(post_dict):
    """
    :param post_dict: The original request.POST item
    :return: The request.POST with some modifications due to caller request format
    """
    translate = {
        '__id__': 'id',
        'name': 'title',
    }

    # copy dict
    result = deepcopy(post_dict)

    # translate keys
    for k in translate.keys():
        if k in post_dict:
            result[translate[k]] = post_dict[k]

    # fix logo
    if 'logo' in result:
        if 'url' in result['logo']:
            result['logo'] = result['logo']['url']

    return result


@csrf_exempt
def project_list(request):
    """
    Methods regarding all project list
    """
    if request.method == 'GET':
        # list existing projects
        return JsonResponse([p.to_json() for p in Project.objects.all()], safe=False)
    elif request.method == 'POST':
        """
        # first fix some incompatibilities in naming
        fields = field_translation(request.POST)

        # create a new project
        form = ProjectForm(fields)
        if form.is_valid():
            instance = form.save()
            return JsonResponse(instance.to_json(), safe=False)
        else:
            return JsonResponse({'error': form.errors}, status=400)
        """
        thread.start_new_thread(fetch_all, ())
        return JsonResponse('', safe=False)
    else:
        # invalid/unsupported HTTP method
        # do not support PUT/DELETE on project list by default to avoid accidents
        return JsonResponse({'error': 'Method %s not allowed on project list' % request.method}, status=403)


def fetch_all():
    from ct_projects.connectors.cloud_teams.cloud_teams import CloudTeamsConnector
    import time

    # wait for the change to take place
    time.sleep(5)
    CloudTeamsConnector().fetch_all()

    # send campaigns
    Campaign.send_all()


@csrf_exempt
def project(request, pk):
    """
    Methods regarding a specific request
    """
    # find project with ID=pk
    try:
        instance = Project.objects.get(pk=int(pk))
    except ObjectDoesNotExist:
        if request.method != 'POST':
            return JsonResponse({'error': 'Project #%d not found' % int(pk)}, status=404)

    if request.method == 'GET':
        # return project info
        return JsonResponse(instance.to_json(), safe=False)
    elif request.method == 'POST':
        """
        # first fix some incompatibilities in naming
        fields = field_translation(json.loads(request.body))

        # update project
        if instance:
            form = ProjectForm(fields, instance=instance)
        else:
            form = ProjectForm(fields)

        if form.is_valid():
            instance = form.save()
            return JsonResponse(instance.to_json(), safe=False)
        else:
            return JsonResponse({'error': form.errors}, status=400)
        """
        thread.start_new_thread(fetch_all, ())
        return JsonResponse('', safe=False)
    elif request.method == 'DELETE':
        # delete project
        instance.delete()
        return JsonResponse({}, status=204)
    else:
        # invalid/unsupported HTTP method
        return JsonResponse({'error': 'Method %s not allowed on project' % request.method}, status=403)


def set_poll_token_status(request, nonce, status):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=400)

    if not nonce:
        return JsonResponse({'error': '`nonce` field is required'}, status=400)

    try:
        poll_token = PollToken.objects.get(token_link__endswith='?nonce=' + nonce)
    except PollToken.DoesNotExist:
        return JsonResponse({'error': 'token for this nonce was not found'}, status=404)

    # set the token status & return OK
    poll_token.status = status
    poll_token.save()

    return JsonResponse({}, status=200)


@csrf_exempt
def update_poll_token(request, nonce):
    return set_poll_token_status(request, nonce, 'USED')


@csrf_exempt
def mark_token_as_completed(request, nonce):
    return set_poll_token_status(request, nonce, 'DONE')


@csrf_exempt
def notify_users(request, pk):
    try:
        Campaign.objects.get(pk=pk).send()
    except Campaign.DoesNotExist:
        Poll.objects.get(pk=pk).send()
    except Poll.DoesNotExist:
        Document.objects.get(pk=pk).send()
    except Document.DoesNotExist:
        return JsonResponse({'error': 'No campaign, poll or document with ID #%d was found' % pk}, status=404)

    return JsonResponse({}, status=200)
