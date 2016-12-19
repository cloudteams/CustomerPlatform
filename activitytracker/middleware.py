from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import render, HttpResponseRedirect, redirect
from social.exceptions import AuthCanceled


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthCanceled:
            return redirect('social-login', action="AuthCancelled")
        else:
            pass


class PreferredRoleCookieMiddleWare(object):
    """
    Middleware to set user preferred role cookie
    If user has picked the "customer" option in the "Who you are" page, remember it
    """

    def process_request(self, request):
        if request.path.lower() == '/projects/login/who-are-you':
            if request.COOKIES.get('cloudteams.preferredRole') == 'customer':
                return redirect('/activitytracker/login/')
            elif request.COOKIES.get('cloudteams.preferredRole') == 'developer':
                return redirect('https://teams.cloudteams.eu/')

    def process_response(self, request, response):
        if not request.COOKIES.get('cloudteams.preferredRole'):
            if request.user.is_authenticated() or \
                            '/activitytracker/account/register' in request.path.lower() or \
                            '/activitytracker/login' in request.path.lower():

                response.set_cookie("cloudteams.preferredRole", 'customer')
            elif '/developer/account/register' in request.path.lower():
                response.set_cookie("cloudteams.preferredRole", 'developer')

        return response
