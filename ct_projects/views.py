from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from ct_projects.connectors.cloud_teams.cloud_teams import CloudTeamsConnector
from ct_projects.models import ProjectFollowing

source = CloudTeamsConnector()


def list_projects(request):
    """
    A list of all projects in cloud teams
    """
    q = request.GET.get('q', '')
    projects = source.list_projects(q)
    pages = Paginator(projects, 2)

    context = {
        'page_obj': pages.page(int(request.GET.get('page', '1'))),
        'q': q,
    }

    return render(request, 'ct_projects/project/all.html', context)


@login_required
def followed_projects(request):
    """
    A list of projects in cloud teams that I follow
    """
    q = request.GET.get('q', '')

    projects = [p for p in source.list_projects(q)
                if ProjectFollowing.objects.filter(user=request.user, project_pk=p.pk)]

    context = {
        'projects': projects,
        'q': q,
    }

    return render(request, 'ct_projects/project/followed.html', context)


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
        return HttpResponse('Only POST allowed', status=400)


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
        return HttpResponse('Only POST allowed', status=400)


def project_details(request, pk):
    # only gets allowed to this method
    if request.method == 'GET':
        # get project
        project = source.get_project(pk)
        if not project:
            return HttpResponse('Project #%s does not exist' % pk, status=403)

        context = {
            'project': project,
        }

        return render(request, 'ct_projects/project/details.html', context)
    else:
        return HttpResponse('Only GET allowed', status=400)
