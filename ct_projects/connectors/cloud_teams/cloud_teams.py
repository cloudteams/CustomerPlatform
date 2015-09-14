from ct_projects.connectors.cloud_teams.server_login import SERVER_URL, USER_PASSWD, XAPI_TEST_FOLDER
from ct_projects.connectors.cloud_teams.xmlrpc_srv import XMLRPC_Server
from ct_projects.models import Project

__author__ = 'dipap'


class CloudTeamsConnector:

    def __init__(self):
        self.srv = XMLRPC_Server(SERVER_URL, USER_PASSWD, verbose=0)
        self.PROJECTS_FOLDER_ID = XAPI_TEST_FOLDER

    def list_projects(self):
        result = []

        entries = self.srv.lst_entries(self.PROJECTS_FOLDER_ID)[1]
        for entry in entries:
            title = entry['title']
            file_type_pos = entry['summary'].find('<span class="label_css">')

            # find description
            description = entry['summary'][:file_type_pos-1]

            # find publisher info
            publisher_start = entry['summary'].rfind('</span>') + len('</span>')
            publisher = entry['summary'][publisher_start + 1:]

            result.append(Project(title=title, description=description, publisher=publisher))

        return result

