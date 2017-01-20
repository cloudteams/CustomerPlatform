# load client
from ct_projects.connectors.cloudcoins.client import CloudCoinsClient

# load entities
from ct_projects.connectors.cloudcoins.base_entity import CloudCoinsApiEntity
from ct_projects.connectors.cloudcoins.projects import CloudCoinsProject
from ct_projects.connectors.cloudcoins.campaigns import CloudCoinsCampaign
from ct_projects.connectors.cloudcoins.users import CloudCoinsCustomer, CloudCoinsProjectManager

# load exceptions
from ct_projects.connectors.cloudcoins.util import CloudCoinsRequestException, CloudCoinsCustomerError, \
    CloudCoinsProjectManagerError, CloudCoinsProjectError, CloudCoinsCampaignError, CloudCoinsCommissionError
