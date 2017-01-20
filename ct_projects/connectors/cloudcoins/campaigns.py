import json

import requests

from ct_projects.connectors.cloudcoins.base_entity import CloudCoinsApiEntity
from ct_projects.connectors.cloudcoins.util import *


class CloudCoinsCampaign(CloudCoinsApiEntity):
    """
    Example Campaign:

    "status": "RUNNING",
    "last_updated": "2017-01-20T14:53:46.416",
    "max_answers": 50,
    "answers": 0,
    "cost": 0,
    "owner": {
        "id": 1,
        "email": "sabine.kolvenbach@fit.fraunhofer.de"
    },
    "id": 77841,
    "answer_value": 5,
    "ends_at": "26-01-2017 17:44",
    "max_cost": 250,
    "created": "2017-01-20T14:53:46.416",
    "project": {
        "id": 30394
    }
    """
    pass


class CampaignService(object):
    """
    Service to manage campaign information
    """

    def __init__(self, endpoint):
        self.endpoint = endpoint + '/campaigns/'

    def get(self, campaign_id):
        response = requests.get('%s%d/' % (self.endpoint, campaign_id))

        if response.status_code < 300:
            return CloudCoinsCampaign(resp=json.loads(response.content))
        else:
            raise CloudCoinsCampaignError('Information for campaign with id %d could not be fetched.' %
                                          campaign_id)

    @staticmethod
    def _get_campaign_data(campaign_obj):
        data = {
            'project_id': campaign_obj.project.id,
            'id': campaign_obj.id,
            'ends_at': timeformat(campaign_obj.expires),
            'answer_value': int(campaign_obj.answer_value) if campaign_obj.answer_value is not None else None,
            'max_answers': campaign_obj.max_answers,
        }

        if campaign_obj.manager:
            data['user_id'] = campaign_obj.manager.pk
            data['user_email'] = campaign_obj.manager.email

        return data

    def post(self, campaign_id, campaign_obj):
        # create campaign
        response = requests.post(self.endpoint,
                                 data=self._get_campaign_data(campaign_obj))

        # return updated campaign object
        if response.status_code < 300:
            return CloudCoinsCampaign(resp=json.loads(response.content))
        else:
            raise CloudCoinsCampaignError('Campaign with id %d could not be created' % campaign_id)

    def update(self, campaign_id, campaign_obj):
        # update campaign
        response = requests.put('%s%d/' % (self.endpoint, campaign_id),
                                data=self._get_campaign_data(campaign_obj))

        # return updated campaign object
        if response.status_code < 300:
            return CloudCoinsCampaign(resp=json.loads(response.content))
        else:
            raise CloudCoinsCampaignError('Campaign with id %d could not be updated' % campaign_id)

    def create_or_update(self, campaign_id, campaign_obj):
        # create campaign if not found on CC service
        # otherwise update existing info

        try:
            self.get(campaign_id)
            campaign = self.update(campaign_id, campaign_obj)
        except CloudCoinsCampaignError:
            campaign = self.post(campaign_id, campaign_obj)

        return campaign

    def add_answer(self, campaign_id, user_id):
        result = requests.post('%s%d/add-answer/' % (self.endpoint, campaign_id), data={
            'user_id': user_id,
        })

        if result.status_code >= 400:
            if 'user has already answered' in json.loads(result.content)['payload'].lower():
                raise CloudCoinsAnswerAlreadyExistsError('Answer already provided')

            raise CloudCoinsCampaignError('Answer could not be added.')

    def stop(self, campaign_id):
        result = requests.post('%s%d/stop/' % (self.endpoint, campaign_id))

        # ignore 400 response
