import thread
from django.core.mail import send_mail
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import Signal
from django.dispatch import receiver
from django.template.loader import render_to_string

from activitytracker.models import User
from ct_projects.models import Campaign, Project, ProjectFollowing, Notification
from profile.lists import *

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class UserProfile(models.Model):
    """
    Additional information about CloudTeams customer account
    Initially will be filled in using the wizard
    """

    # Link to user in Activity Tracker
    user = models.OneToOneField(User)

    # Avatar
    profile_picture = models.ImageField(upload_to='avatars/', blank=True, null=True, default=None)

    # Generic info
    first_name = models.CharField(max_length=255, blank=True, null=True, default=None)
    last_name_initial = models.CharField(max_length=1, blank=True, null=True, default=None)
    year_of_birth = models.IntegerField(blank=True, null=True, default=None, validators=[MinValueValidator(1930),
                                                                                         MaxValueValidator(2010)])
    # -- location is in main model -> asume it to be home location

    # Business info
    education = models.CharField(max_length=127, blank=True, default='', choices=EDUCATION_LEVELS)
    employment_status = models.CharField(max_length=127, blank=True, default='', choices=EMPLOYMENT_STATUS_OPTIONS)
    business_sector = models.CharField(max_length=127, blank=True, default='', choices=BUSINESS_SECTORS)
    work_position = models.CharField(max_length=127, blank=True, default='', choices=WORK_POSITIONS)
    work_location = models.CharField(max_length=255, blank=True, default='')
    years_experience = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])

    # Tech level
    tech_level = models.CharField(max_length=31, blank=True, default='', choices=TECH_LEVELS)

    # Check if the profile wizard has run at least once
    has_been_saved = models.BooleanField(default=False, editable=False)

    # email notification setting
    email_notifications = models.BooleanField(default=True)

    def get_display_name(self):
        if self.first_name and self.last_name_initial:
            return '%s %s.' % (self.first_name, self.last_name_initial)
        elif self.first_name:
            return self.first_name
        else:
            return self.user.username

    def get_completion_progress(self):
        """
        :return: A percentage ("00" - "100") indicating how much of the profile info has been completed
        """
        points = 0

        if self.profile_picture:
            points += 5

        if self.first_name:
            points += 4

        if self.last_name_initial:
            points += 1

        if self.year_of_birth:
            points += 5

        if self.business_sector:
            points += 5

        if self.work_location:
            points += 5

        if self.years_experience:
            points += 5

        if self.tech_level:
            points += 15

        if self.user.devices.exists():
            points += 20

        if self.user.platforms.exists():
            points += 20

        if self.user.brand_opinions.exists():
            points += 15

        return points

    def avatar(self):
        if not self.profile_picture:
            return None
        else:
            return '/media/avatars/' + self.profile_picture.name.split('/')[-1]

    def list_platforms(self):
        return [platform.platform for platform in self.user.platforms.all()]

    def list_devices(self):
        return [device.device for device in self.user.devices.all()]

    def list_interests(self):
        return [interest.interest for interest in self.user.interests.all()]


class Influence(models.Model):
    user = models.ForeignKey(User, related_name='influences')
    influence = models.CharField(max_length=255, choices=INFLUENCES)


class DeviceUsage(models.Model):
    user = models.ForeignKey(User, related_name='devices')
    device = models.CharField(max_length=255, choices=DEVICES)


class PlatformUsage(models.Model):
    user = models.ForeignKey(User, related_name='platforms')
    platform = models.CharField(max_length=255, choices=PLATFORMS)


class UserInterest(models.Model):
    user = models.ForeignKey(User, related_name='interests')
    interest = models.CharField(max_length=255, choices=INTERESTS)


class UserBrandOpinion(models.Model):
    user = models.ForeignKey(User, related_name='brand_opinions')
    brand = models.CharField(max_length=16)
    opinion = models.CharField(max_length=1, choices=BRAND_OPINIONS)


def on_profile_info_updated(sender, instance, created, **kwargs):

    def send_all_campaigns():
        Campaign.send_all()

    # send campaigns asynchronously
    thread.start_new_thread(send_all_campaigns, ())


# connect with update events
post_save.connect(on_profile_info_updated, sender=UserProfile)
post_save.connect(on_profile_info_updated, sender=Influence)
post_save.connect(on_profile_info_updated, sender=DeviceUsage)
post_save.connect(on_profile_info_updated, sender=PlatformUsage)
post_save.connect(on_profile_info_updated, sender=UserBrandOpinion)


class PlatformInvitation(models.Model):
    """
    An invitation from a CloudTeams user to an email
    """
    user = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    status = models.CharField(max_length=15, choices=INVITATION_STATUS, default='PENDING')

platform_invitation_accepted = Signal(providing_args=["invitation"])


class TeamInvitation(models.Model):
    """
    An invitation from a CloudTeams team (project) to an email
    """
    project_id = models.IntegerField()
    email = models.EmailField()
    auto_accept = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=INVITATION_STATUS, default='PENDING')

    def send_email(self):
        # render the email
        project_name = Project.objects.get(id=self.project_id).title
        title = 'Invitation from %s: Join CloudTeams.eu today!' % project_name

        ctx = {
            'title': title,
            'project_name': project_name,
            'team_ref_id': self.pk,
        }

        plain_content = render_to_string('profile/emails/invitation-plaintext.txt', ctx)
        html_content = render_to_string('profile/emails/invitation.html', ctx)

        # send the email
        send_mail(subject=title, message=plain_content, html_message=html_content,
                  from_email='webmasters@cloudteams.eu',
                  recipient_list=[self.email], fail_silently=False)

    def save(self, *args, **kwargs):
        if self.status == 'ACCEPTED':
            # get invited user
            user = User.objects.get(email=self.email)

            try:
                project = Project.objects.get(id=self.project_id)

                if self.auto_accept:
                    # create following relationship to project
                    if not user.follows.filter(project_id=self.project_id).exists():
                        ProjectFollowing.objects.create(user=user, project=project)
                else:
                    # send notification to user
                    project_url = '/projects/%d/' % project.id
                    project_link = '<a href="%s" target="_blank">%s</a>' % (project_url, project.title)
                    Notification.objects.create(user=user, text='You were invited to follow project %s.' % project_link,
                                                custom_action='FOLLOW %d' % project.id, custom_action_text='Accept',
                                                dismiss_action='Reject')
            except Project.DoesNotExist:
                # project might have been deleted in the meanwhile
                pass

        super(TeamInvitation, self).save(*args, **kwargs)


@receiver(post_save, sender=User)
def on_user_signup(sender, instance, created, **kwargs):
    # only on signup
    if created:
        # check if the signup is from a user who was invited
        if PlatformInvitation.objects.filter(email=instance.email, status='PENDING').exists():
            # accept the invitation
            invitation = PlatformInvitation.objects.get(email=instance.email, status='PENDING')
            invitation.status = 'ACCEPTED'
            invitation.save()

            # send the signal
            platform_invitation_accepted.send(sender=PlatformInvitation, invitation=invitation)

        for invitation in TeamInvitation.objects.filter(email=instance.email, status='PENDING'):
            # accept the invitation
            invitation.status = 'ACCEPTED'
            invitation.save()

