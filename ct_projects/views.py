from django.shortcuts import render
from ct_projects.connectors.cloud_teams.cloud_teams import CloudTeamsConnector

source = CloudTeamsConnector()


def list_projects(request):
    context = {
        'projects': source.list_projects(),
    }

    return render(request, 'ct_projects/project/all.html', context)
