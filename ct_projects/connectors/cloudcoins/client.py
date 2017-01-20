from ct_projects.connectors.cloudcoins.campaigns import CampaignService
from ct_projects.connectors.cloudcoins.commissions import CommissionService
from ct_projects.connectors.cloudcoins.projects import ProjectService
from ct_projects.connectors.cloudcoins.users import CustomerService, ProjectManagerService


class CloudCoinsClient(object):
    endpoint = 'https://customers.cloudteams.eu/cloudcoins/api'

    def __init__(self):
        self.users = CustomerService(self.endpoint)
        self.project_managers = ProjectManagerService(self.endpoint)
        self.projects = ProjectService(self.endpoint)
        self.campaigns = CampaignService(self.endpoint)
        self.commission = CommissionService(self.endpoint)

