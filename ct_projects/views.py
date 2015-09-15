from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from ct_projects.connectors.cloud_teams.cloud_teams import CloudTeamsConnector
from ct_projects.models import ProjectFollowing

source = CloudTeamsConnector()


def list_projects(request):
    context = {
        'projects': source.list_projects(),
    }

    return render(request, 'ct_projects/project/all.html', context)


@login_required
def follow_project(request, pk):
    # only posts allowed to this method
    if request.method == 'POST':
        # get project
        project = source.get_project(pk)
        if not project:
            return HttpResponse('Project #%s does not exist' % pk, status=403)

        # check if already followed
        if ProjectFollowing.objects.filter(project_pk=pk, user=request.user):
            return HttpResponse('You are already following project #%s' % pk, status=403)

        # follow & return OK
        ProjectFollowing.objects.create(project_pk=pk, user=request.user)
        return redirect(reverse('all-projects'))
    else:
        return HttpResponse('Only POST allowed', status=403)


@login_required
def unfollow_project(request, pk):
    # only posts allowed to this method
    if request.method == 'POST':
        # get project
        project = source.get_project(pk)
        if not project:
            return HttpResponse('Project #%s does not exist' % pk, status=403)

        # check if actually followed
        pfs = ProjectFollowing.objects.filter(project_pk=pk, user=request.user)
        if not pfs:
            return HttpResponse('You are not following project #%s' % pk, status=403)

        # unfollow & return OK
        pfs.delete()
        return redirect(reverse('all-projects'))
    else:
        return HttpResponse('Only POST allowed', status=403)
