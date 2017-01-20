import json

import requests

from ct_projects.connectors.cloudcoins.base_entity import CloudCoinsApiEntity
from ct_projects.connectors.cloudcoins.campaigns import CloudCoinsCampaign
from ct_projects.connectors.cloudcoins.util import *


class CloudCoinsProject(CloudCoinsApiEntity):
    """
    Example Project:

    "owners": [],
    "max_cost": 250,
    "max_answers": 50,
    "answers": 0,
    "cost": 0,
    "id": 30394
    "campaigns": None if not with_campaigns, [CloudCoinsCampaign1, CloudCoinsCampaign2, ...] otherwise
    """
    def __init__(self, resp):
        super(CloudCoinsProject, self).__init__(resp)

        self.campaigns = None


class ProjectService(object):
    """
    Service to manage project information
    """

    def __init__(self, endpoint):
        self.endpoint = endpoint + '/projects/'

    def get(self, project_id, with_campaigns=True):
        response = requests.get('%s%d/' % (self.endpoint, project_id))

        if response.status_code >= 400:
            raise CloudCoinsProjectError(
                'Information for project with id %d could not be fetched.' % project_id)

        project = CloudCoinsProject(resp=json.loads(response.content))

        if with_campaigns:
            # also load project campaigns
            response = requests.get('%s%d/campaigns/' % (self.endpoint, project_id))

            project.campaigns = []
            for c_entry in json.loads(response.content)['payload']:
                project.campaigns.append(CloudCoinsCampaign({
                    'payload': c_entry
                }))

        return project

    def delete_campaigns(self, project_id):
        response = requests.delete('%s%d/campaigns/' % (self.endpoint, project_id))

        if response.status_code >= 400:
            raise CloudCoinsProjectError('Could not delete project with id %d' % project_id)
