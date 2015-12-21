from datetime import datetime
from django.utils.timezone import now
from ct_projects.connectors.cloud_teams.server_login import SERVER_URL, USER_PASSWD, XAPI_TEST_FOLDER
from ct_projects.connectors.cloud_teams.xmlrpc_srv import XMLRPC_Server
from ct_projects.models import Project

__author__ = 'dipap'


class CloudTeamsConnector:

    def __init__(self):
        self.srv = XMLRPC_Server(SERVER_URL, USER_PASSWD, verbose=0)
        self.PROJECTS_FOLDER_ID = XAPI_TEST_FOLDER
        self.projects = None
        self.latest_update_on = now()

    def fetch_projects(self):
        """
        Populates Customer Platform DB with projects from the Teams Platform
        :return: Number of projects fetched from CloudTeams team platform
        """
        entries = self.srv.get_projectstore('')
        for entry in entries:
            project = Project()
            project.id = entry['__id__']
            current = Project.objects.filter(pk=project.id)
            if current:
                project = current[0]

            project.title = entry['name']
            project.description = entry['description'] if 'description' in entry else ''
            project.application_type = entry['bscw_cloudteams:p_type']
            project.logo = entry['bscw_cloudteams:p_logo'] if 'bscw_cloudteams:p_logo' in entry else ''
            project.rewards = entry['rewards'] if 'rewards' in entry else ''
            project.category = entry['bscw_cloudteams:p_category']
            project.managers = ','.join(entry['managers']) if 'managers' in entry else ''
            project.members = ','.join(entry['members']) if 'members' in entry else ''
            project.is_public = entry['is_public'] if 'is_public' in entry else False
            project.created = datetime.fromtimestamp(int(entry['ctime']))

            # save the project in the database
            project.save()

        return len(entries)
