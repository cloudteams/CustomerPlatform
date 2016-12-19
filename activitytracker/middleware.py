from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import render, HttpResponseRedirect, redirect
from social.exceptions import AuthCanceled, AuthAlreadyAssociated


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthCanceled:
            return redirect('social-login', action="AuthCancelled")
        elif type(exception) == AuthAlreadyAssociated:
            return redirect('social-login', action="AuthAlreadyAssociated")
            pass
