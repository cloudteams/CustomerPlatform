from django.contrib import admin
from profile.models import *


class PlatformInvitationAdmin(admin.ModelAdmin):
    pass

admin.site.register(PlatformInvitation, PlatformInvitationAdmin)
