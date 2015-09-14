from django.db import models


# The project is not a typical Django model as it's not saved on the CloudTeams community site but on BSCW
class Project:

    def __init__(self, pk, title, description, publisher):
        self.pk = pk
        self.title = title
        self.description = description
        self.publisher = publisher

    def __unicode__(self):
        return '#%d - %s' % (self.pk, self.title)
