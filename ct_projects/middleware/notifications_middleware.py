class NotificationsMiddleware(object):

    # Inject unread notifications to user
    def process_request(self, request):
        if request.user.is_authenticated():
            # get persistent notifications
            request.user.unread_notifications = list(request.user.notifications.filter(seen=False, persistent=True))

            # get inline notifications
            qs = request.user.notifications.filter(persistent=False, seen=False)
            notifications = list(qs)
            qs.update(seen=True)
            request.user.inline_notifications = notifications
