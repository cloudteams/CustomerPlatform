from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import render, HttpResponseRedirect, redirect
from social.exceptions import AuthCanceled


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthCanceled:
            return redirect('social-login', action="AuthCancelled")
        else:
            pass
