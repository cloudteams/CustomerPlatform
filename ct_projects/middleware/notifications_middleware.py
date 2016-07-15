class NotificationsMiddleware(object):

    # Inject unread notifications to user
    def process_request(self, request):
        if request.user.is_authenticated():
            request.user.unread_notifications = list(request.user.notifications.filter(seen=False))
