import json

import requests

from ct_projects.connectors.cloudcoins.base_entity import CloudCoinsApiEntity
from ct_projects.connectors.cloudcoins.util import *


class CloudCoinsCustomer(CloudCoinsApiEntity):
    """
    balance: 15,
    last_updated: "2017-01-20T17:27:14.155",
    id: 9515,
    email: ""
    """
    pass


class CloudCoinsProjectManager(CloudCoinsApiEntity):
    """
    "max_cost": 262,
    "max_answers": 52,
    "answers": 2,
    "cost": 12,
    "id": 1,
    "projects": [
        {
            "id": 1
        },
        {
            "id": 30394
        }
    ]
    """
    pass


class CustomerService(object):
    """
    Service to manage and get customer information
    """

    def __init__(self, endpoint):
        self.endpoint = endpoint + '/customers/'

    def get(self, customer_id):
        response = requests.get('%s%d/' % (self.endpoint, customer_id))

        if response.status_code < 300:
            return CloudCoinsCustomer(resp=json.loads(response.content))
        elif response.status_code == 404:  # user info still not passed to CC service - no balance for this user
            return CloudCoinsCustomer(resp={
                'payload': {
                    'balance': 0
                }
            })
        else:
            raise CloudCoinsCustomerError('Information for customer with id %d could not be fetched.' % customer_id)


class ProjectManagerService(object):
    """
    Service to manage and get project manager information
    """

    def __init__(self, endpoint):
        self.endpoint = endpoint + '/users/'

    def get(self, manager_id):
        response = requests.get('%s%d/' % (self.endpoint, manager_id))

        if response.status_code < 300:
            return CloudCoinsProjectManager(resp=json.loads(response.content))
        else:
            raise CloudCoinsProjectManagerError('Information for project manager with id %d could not be fetched.' %
                                                manager_id)
