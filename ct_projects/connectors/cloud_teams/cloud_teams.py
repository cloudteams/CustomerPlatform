from datetime import datetime

import pytz
from django.utils.timezone import now
from django_comments.models import Comment

from Activitytracker_Project.settings import SITE_ID
from ct_projects.connectors.cloud_teams.server_login import SERVER_URL, USER_PASSWD, XAPI_TEST_FOLDER, CUSTOMER_PASSWD
from ct_projects.connectors.cloud_teams.xmlrpc_srv import XMLRPC_Server
from ct_projects.models import Project, Campaign, Document, Poll, Idea

__author__ = 'dipap'


class CloudTeamsConnector:

    def __init__(self):
        self.srv = XMLRPC_Server(SERVER_URL, CUSTOMER_PASSWD, verbose=0)
        self.PROJECTS_FOLDER_ID = XAPI_TEST_FOLDER
        self.projects = None
        self.latest_update_on = now()

    def fetch_all(self):
        """
        Populates Customer Platform DB with projects from the Teams Platform
        :return: Number of projects fetched from CloudTeams team platform
        """
        entries = self.srv.get_projectstore('')

        project_ids = []
        campaign_ids = []
        document_ids = []
        poll_ids = []

        for entry in entries:
            project = Project()
            project.id = int(entry['__id__'])
            project_ids.append(project.id)
            current = Project.objects.filter(pk=project.id)
            if current:
                project = current[0]

            project.title = entry['name']
            project.description = entry['descr'] if 'descr' in entry else ''
            project.application_type = entry['bscw_cloudteams:p_type']
            project.logo = entry['logo']['url'] if 'logo' in entry else ''
            project.rewards = entry['rewards'] if 'rewards' in entry else ''
            project.category = entry['bscw_cloudteams:p_category']
            project.icon = entry['category_icon'] if 'category_icon' in entry else ''
            project.managers = ','.join(entry['managers']) if 'managers' in entry else ''
            project.members = ','.join(entry['members']) if 'members' in entry else ''
            project.is_public = entry['is_public'] if 'is_public' in entry else False
            project.created = datetime.fromtimestamp(int(entry['ctime'])) if 'ctime' in entry else now()

            # save the project in the database
            project.save()

            # get developer comments
            if 'customer_ideas' in entry:
                for c_idea in entry['customer_ideas']:
                    # validation
                    if 'title' not in c_idea:
                        continue

                    if 'desc' not in c_idea:
                        c_idea['desc'] = ''

                    print c_idea
                    # find the idea in the customer platform
                    try:
                        idea = Idea.objects.get(project_id=project.pk, title=c_idea['title'],
                                                description=c_idea['desc'])
                    except Idea.DoesNotExist:
                        print 'Idea "%s" on project %d not found' % (c_idea['title'], project.pk)
                        continue

                    if 'replies' in c_idea:
                        # add or update developer replies
                        comments = list(idea.comments.all())

                        for c_reply in c_idea['replies']:
                            # try to find
                            found = False
                            for comment in comments:
                                if comment.comment == c_reply['title'] and comment.user_name == c_reply['author']:
                                    found = True
                                    break

                            # create new comment
                            if not found:
                                submit_date = datetime.utcfromtimestamp(c_reply['timestamp']).replace(tzinfo=pytz.timezone('CET'))
                                comment = Comment.objects.create(user_name=c_reply['author'],
                                                                 user_email=c_reply['author_email'],
                                                                 comment=c_reply['title'], content_object=idea,
                                                                 site_id=SITE_ID, submit_date=submit_date)
                                comments.append(comment)

            # get all project campaigns
            if 'campaigns' in entry:
                for c_entry in entry['campaigns']:
                    campaign = Campaign()
                    campaign.id = int(c_entry['__id__'])
                    campaign_ids.append(campaign.id)
                    current = Campaign.objects.filter(pk=campaign.id)
                    if current:
                        campaign = current[0]

                    # fill in campaign info
                    campaign.name = c_entry['name']
                    campaign.description = c_entry['descr'] if 'descr' in c_entry else ''
                    campaign.logo = c_entry['logo']['url'] if 'logo' in c_entry else ''
                    campaign.starts = datetime.strptime(c_entry['start'], '%Y-%m-%d %H:%M:%S') if 'start' in c_entry else now()
                    campaign.expires = datetime.strptime(c_entry['end'], '%Y-%m-%d %H:%M:%S') if ('end' in c_entry) and (c_entry['end'] != 'Never') else None
                    campaign.rewards = c_entry['rewards'] if 'rewards' in c_entry else ''
                    campaign.project = project

                    # save the campaign in the database
                    campaign.save()

                    # add all campaign documents
                    if 'documents' in c_entry:
                        for d_entry in c_entry['documents']:
                            document = Document()

                            id_key = '__id__'
                            if id_key not in d_entry:
                                id_key = 'id'

                            document.id = int(d_entry[id_key])
                            document_ids.append(document.id)
                            current = Document.objects.filter(pk=document.id)
                            if current:
                                document = current[0]

                            # fill in document info
                            document.name = d_entry['name']
                            document.link = d_entry['url']
                            document.description = d_entry['descr'] if 'descr' in d_entry else ''
                            document.campaign = campaign

                            # save the document in the database
                            document.save()

                    # add all campaign polls
                    if 'polls' in c_entry:
                        for p_entry in c_entry['polls']:
                            poll = Poll()
                            poll.id = int(p_entry['__id__'])
                            poll_ids.append(poll.id)
                            current = Poll.objects.filter(pk=poll.id)
                            if current:
                                poll = current[0]

                            # fill in poll info
                            poll.name = p_entry['name']
                            poll.description = p_entry['descr'] if 'descr' in p_entry else ''
                            poll.campaign = campaign

                            # save the poll in the database
                            poll.save()

        # deleting objects not found in Team Platform
        Project.objects.all().exclude(id__in=project_ids).delete()
        Campaign.objects.all().exclude(id__in=campaign_ids).delete()
        Document.objects.all().exclude(id__in=document_ids).delete()
        Poll.objects.all().exclude(id__in=poll_ids).delete()

        return len(entries)
