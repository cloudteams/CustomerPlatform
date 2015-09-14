from django.db import models


# The project is not a typical Django model as it's not saved on the CloudTeams community site but on BSCW
class Project:

    def __init__(self, title, description, publisher):
        self.title = title
        self.description = description
        self.publisher = publisher

    def __unicode__(self):
        return self.title
