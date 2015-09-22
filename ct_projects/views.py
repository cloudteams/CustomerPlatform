from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
import django_comments
from django_comments.forms import CommentForm
from django_comments.models import Comment
from ct_projects.connectors.cloud_teams.cloud_teams import CloudTeamsConnector
from ct_projects.forms import IdeaForm, IdeaRatingForm
from ct_projects.models import ProjectFollowing, Idea

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
            return HttpResponse('Project #%s does not exist' % pk, status=404)

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
            return HttpResponse('Project #%s does not exist' % pk, status=404)

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
    """
    View the details page of a specific project
    """
    # only gets allowed to this method
    if request.method == 'GET':
        # get project
        project = source.get_project(pk)
        if not project:
            return HttpResponse('Project #%s does not exist' % pk, status=404)

        context = {
            'project': project,
        }

        return render(request, 'ct_projects/project/details.html', context)
    else:
        return HttpResponse('Only GET allowed', status=400)


@login_required
def post_idea(request, pk):
    """
    Post a new idea on a project
    """
    # get project
    project = source.get_project(pk)
    if not project:
        return HttpResponse('Project #%s does not exist' % pk, status=404)

    context = {
        'project': project
    }
    status = 200

    if request.method == 'GET':
        context['form'] = IdeaForm()
    elif request.method == 'POST':
        form = IdeaForm(request.POST)

        if form.is_valid():
            # save the idea
            idea = form.save(commit=False)
            idea.user = request.user
            idea.project_pk = project.pk
            idea.save()

            # redirect to project home page
            return redirect(reverse('project-details', args=(pk, )))
        else:
            context['form'] = form
            status = 400
    else:
        return HttpResponse('Only GET,POST allowed', status=400)

    return render(request, 'ct_projects/project/post-idea.html', context, status=status)


class IdeaDetailView(DetailView):
    model = Idea
    template_name = 'ct_projects/idea/details.html'
    context_object_name = 'idea'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)

        idea = context['idea']
        context['comment_form'] = CommentForm(idea)
        context['project'] = source.get_project(str(idea.project_pk))
        return context

idea_details = IdeaDetailView.as_view()


def comment_posted(request):
    if request.GET['c']:
        comment_id = request.GET['c']
        comment = Comment.objects.get(pk=comment_id)
        idea = Idea.objects.get(id=comment.object_pk)
        if idea:
            return redirect(reverse('idea-details', args=(idea.project_pk, idea.pk)))


@login_required
def rate_idea(request, project_pk, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.method == 'POST':
        if idea.ratings.filter(user=request.user):
            return HttpResponseForbidden('You can not rate more than once')

        # save the rating
        form = IdeaRatingForm(request.POST)
        rating = form.save(commit=False)
        rating.user = request.user
        rating.idea = idea
        rating.save()

        return redirect(reverse('idea-details', args=(idea.project_pk, idea.pk)))
    else:
        return HttpResponse('Only POST allowed', status=400)
