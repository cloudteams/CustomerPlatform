from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from django_comments.forms import CommentForm
from django_comments.models import Comment
from ct_projects.forms import IdeaForm, IdeaRatingForm
from ct_projects.models import ProjectFollowing, Idea, Project, Campaign, Poll, PollToken


def how_it_works(request):
    return render(request, 'ct_projects/how-it-works.html', {
        'light_menu': True,
    })


def list_projects(request):
    """
    A list of all projects in cloud teams
    """
    q = request.GET.get('q', '')
    qs = Project.objects.filter(Q(title__icontains=q) | Q(description__icontains=q) |
                                Q(category__icontains=q))

    # ordering
    order = request.GET.get('order', 'most-popular')
    if order == 'most-popular':
        qs = qs.annotate(num_followers=Count('followed')).order_by('-num_followers', '-created')
    else:
        order = 'latest'
        qs = qs.order_by('-created')

    pages = Paginator(qs, 12)

    context = {
        'n_of_projects': Project.objects.all().count(),
        'page_obj': pages.page(int(request.GET.get('page', '1'))),
        'q': q,
        'order': order,
        'light_menu': not request.user.is_authenticated(),
    }

    return render(request, 'ct_projects/project/all.html', context)


@login_required
def followed_projects(request):
    """
    A list of projects in cloud teams that I follow
    """
    q = request.GET.get('q', '')

    n_of_followed = ProjectFollowing.objects.filter(user=request.user).count()
    projects = [f.project for f in ProjectFollowing.objects.filter(user=request.user)]

    context = {
        'projects': projects,
        'n_of_followed': n_of_followed,
    }

    return render(request, 'ct_projects/project/dashboard.html', context)


@login_required
def followed_campaigns(request):
    """
    A list of projects in cloud teams that I follow
    """
    projects = [f.project for f in ProjectFollowing.objects.filter(user=request.user)]
    campaigns = []
    for p in projects:
        campaigns += p.get_running_campaigns()

    context = {
        'campaigns': campaigns,
        'n_of_followed': len(campaigns),
    }

    return render(request, 'ct_projects/campaign/dashboard.html', context)


@login_required
def follow_project(request, pk):
    # only posts allowed to this method
    if request.method == 'POST':
        # get project
        project = Project.objects.get(pk=pk)
        if not project:
            return HttpResponse('Project #%d does not exist' % pk, status=404)

        # check if already followed
        if ProjectFollowing.objects.filter(project=project, user=request.user):
            return HttpResponse('You are already following project #%d' % pk, status=403)

        # follow & return OK
        ProjectFollowing.objects.create(project=project, user=request.user)
        return redirect(reverse('project-details', args=(pk, )))
    else:
        return HttpResponse('Only POST allowed', status=400)


@login_required
def unfollow_project(request, pk):
    # only posts allowed to this method
    if request.method == 'POST':
        # get project
        project = Project.objects.get(pk=pk)
        if not project:
            return HttpResponse('Project #%d does not exist' % pk, status=404)

        # check if actually followed
        pfs = ProjectFollowing.objects.filter(project=project, user=request.user)
        if not pfs:
            return HttpResponse('You are not following project #%d' % pk, status=403)

        # unfollow & return OK
        pfs.delete()
        return redirect(reverse('project-details', args=(pk, )))
    else:
        return HttpResponse('Only POST allowed', status=400)


def project_details(request, pk):
    """
    View the details page of a specific project
    """
    # only gets allowed to this method
    if request.method == 'GET':
        # get project
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404()

        if not project:
            return HttpResponse('Project #%d does not exist' % pk, status=404)

        context = {
            'project': project,
            'idea_form': IdeaForm(),
        }

        if request.GET.get('tab', '') == 'ideas':
            context['tab'] = 'ideas'

        return render(request, 'ct_projects/project/details.html', context)
    else:
        return HttpResponse('Only GET allowed', status=400)


@login_required
def post_idea(request, pk):
    """
    Post a new idea on a project
    """
    # get project
    project = Project.objects.get(pk=pk)
    if not project:
        return HttpResponse('Project #%d does not exist' % pk, status=404)

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
            idea.project = project
            idea.save()

            # redirect to project home page
            return redirect(reverse('project-details', args=(pk, )) + '?tab=ideas')
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
        context['project'] = idea.project
        return context

idea_details = IdeaDetailView.as_view()


def comment_posted(request):
    if request.GET['c']:
        comment_id = request.GET['c']
        comment = Comment.objects.get(pk=comment_id)
        idea = Idea.objects.get(id=comment.object_pk)
        if idea:
            return redirect(reverse('idea-details', args=(idea.project.pk, idea.pk)))


@login_required
def rate_idea(request, project_pk, pk):
    idea = get_object_or_404(Idea, pk=pk)

    if request.method == 'POST':
        if idea.ratings.filter(user=request.user):
            # unlike
            idea.ratings.filter(user=request.user).delete()

            return redirect(reverse('project-details', args=(idea.project.pk,)) + '?tab=ideas')

        # save the rating
        form = IdeaRatingForm(request.POST)
        rating = form.save(commit=False)
        rating.user = request.user
        rating.idea = idea
        rating.save()

        return redirect(reverse('project-details', args=(idea.project.pk, )) + '?tab=ideas')
    else:
        return HttpResponse('Only POST allowed', status=400)


class CampaignDetailView(DetailView):
    model = Campaign
    template_name = 'ct_projects/campaign/details.html'
    context_object_name = 'campaign'

    def get_context_data(self, **kwargs):
        ctx = super(CampaignDetailView, self).get_context_data(**kwargs)
        ctx['idea_form'] = IdeaForm()
        return ctx

campaign_details = CampaignDetailView.as_view()


@login_required
def request_poll_token(request, project_pk, pk):
    poll = get_object_or_404(Poll, pk=pk)
    return redirect(poll.get_poll_token_link(request.user))


# Project generic views
def terms_and_conditions(request):
    return render(request, 'ct_projects/generic/terms-and-conditions.html')


def privacy_policy(request):
    return render(request, 'ct_projects/generic/privacy-policy.html')
