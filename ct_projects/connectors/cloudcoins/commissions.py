import json

import requests
from decimal import Decimal

from ct_projects.connectors.cloudcoins.util import *


class CommissionService(object):
    """
    Service to retrieve commission information
    """

    def __init__(self, endpoint):
        self.endpoint = endpoint + '/cloudteams/commission/'

    def get(self):
        response = requests.get(self.endpoint)

        try:
            return Decimal(json.loads(response.content)['payload']['commision'])
        except (ValueError, KeyError):
            raise CloudCoinsCommissionError('Could not retrieve CloudTeams Commission.')